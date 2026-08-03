# 카카오 소셜 로그인 — 백엔드 하네스

Flutter 앱이 카카오 SDK로 받은 토큰을 **백엔드가 검증하고 자체 JWT를 발급**하는
경로에 대한 작업 지시서. 모바일 세션과 웹 세션을 **분리 관리**하는 것이 핵심 요구사항이다.

클라이언트(플러터) 쪽 절차 ---> [`../../pmh_flutter/_docs/flutter-kakao-oauth-harness.md`](../../pmh_flutter/_docs/flutter-kakao-oauth-harness.md)
인증 게이트웨이 분리 배포 ---> [`../apps/auth/_docs/auth-gateway-harness.md`](../apps/auth/_docs/auth-gateway-harness.md)
백엔드 영역 지침 ---> [`../CLAUDE.md`](../CLAUDE.md)

> **구현·배포 완료(2026-08-03).** 갤럭시 노트9 실기기에서 카카오 로그인 →
> 세션 생성까지 종단 확인했다. 이 문서는 착수 시점의 지시서에서 출발해 실제 결정과
> 결과를 반영해 갱신한 것이며, 문서와 코드가 어긋나면 **코드가 정본**이다.

---

## 1. 현재 저장소 상태 — 원안 프롬프트와 다른 지점

원안 지시서는 "Redis 컨테이너 추가", "hexagonal infrastructure 레이어",
`/api/v1/auth/...` 경로를 전제했다. **이 저장소는 이미 그보다 앞서 있다.**
아래는 코드를 읽고 확인한 사실이며, 문서와 코드가 어긋나면 **코드가 정본**이다.

| 원안의 전제 | 이 저장소의 실제 | 결론 |
|---|---|---|
| docker-compose에 Redis 추가 필요 | 이미 있음 — `redis:7-alpine`, `6379`, `redis_data` 볼륨 + `--appendonly yes` ([`docker-compose.yaml`](../../docker-compose.yaml)) | **작업 불필요.** 재사용한다 |
| `.env`에 `REDIS_HOST`/`PORT`/`DB` 추가 | 코드는 `REDIS_URL` **단일 변수**를 읽는다 (`RefreshTokenStore.__init__`, 기본 `redis://localhost:6379/0`) | 쪼개지 말고 `REDIS_URL` 유지 |
| 인증을 백엔드(`main.py`)에 구현 | 인증은 **별도 컨테이너** `auth`(`auth_main.py`, :9000)에서만 발급. 백엔드는 공개키로 **검증만** 한다 | 신규 엔드포인트는 `apps/auth/` 아래에 추가 |
| 경로 `/api/v1/auth/kakao/mobile` | `auth_main.py`가 라우터를 `/auth` prefix로 마운트 → 실제 경로는 **`POST /auth/kakao/mobile`** (auth 호스트 :9000) | §3 표 참조 |
| hexagonal architecture infrastructure 레이어 | `apps/auth`는 헥사고날이 **아니다**. `router.py` / `services.py` / `schemas.py` / `rbac.py` 평면 구조 (헥사고날은 `apps/titanic`) | 기존 평면 구조를 따른다 |
| 카카오 검증 서비스 신규 구현 | [`core/matrix/kakao_oauth_client.py`](../core/matrix/kakao_oauth_client.py)가 이미 있다 — 단 **웹 code 교환 흐름 전용** | §4.1 — 함수만 추가 |
| Redis 키 `auth:mobile:*` / `auth:web:*` | 기존 웹 세션이 이미 `authgw:refresh:{jti}` 로 살아 있다 (`apps/auth/services.py`) | §2.1에서 재조정 |

### 1.1 이미 동작 중인 웹 인증 흐름 (건드리지 말 것)

```
POST /auth/login            → provider 인증 URL 발급
GET  /auth/callback/kakao   → code 교환 → userinfo → JWT 쌍 발급 → 쿠키 설정
POST /auth/refresh          → 리프레시 로테이션(재사용 감지 시 해당 sub 세션 전체 폐기)
POST /auth/logout           → 쿠키 정리 + Redis revoke
GET  /auth/.well-known/jwks.json
```

- 토큰은 **RS256 비대칭**. 개인키(`JWT_PRIVATE_KEY`)는 `auth` 컨테이너에만 존재한다.
- access token 수명 10분(`_ACCESS_TOKEN_EXPIRES_MIN`), refresh 14일
  (`REFRESH_TOKEN_TTL_SECONDS`). 이 값은 `core.security.create_refresh_token`의
  기본값과 **수동 동기화 상태**다 — 한쪽만 바꾸면 토큰 만료와 Redis TTL이 어긋난다.
- 웹의 `sub`는 **이메일**이다. 별도 users 테이블도 `user_id`도 인증 경로에 없다.
  **모바일은 이메일을 쓸 수 없어 `kakao:{회원번호}`를 `sub`로 쓴다** → §6-Q1.

---

## 2. Redis 스키마 — 모바일/웹 분리

### 2.1 원안과의 재조정

원안은 `auth:mobile:*` / `auth:web:*` 두 네임스페이스를 **새로** 만들자고 한다.
그러나 웹 세션은 이미 `authgw:refresh:*`에 저장돼 운영 중이고, 이를 옮기면
**배포되는 순간 기존 로그인 세션이 전부 끊긴다.** 따라서:

- **웹**: 기존 `authgw:refresh:*` 를 그대로 둔다. 마이그레이션하지 않는다.
- **모바일**: 새 네임스페이스 `authgw:mobile:*` 를 추가한다.
  (원안의 `auth:` 대신 `authgw:` — 같은 Redis를 온톨로지 크롤러가 `crawler:target:*`로
  쓰고 있어 인증 키는 `authgw:` 하나로 모으는 것이 기존 규약이다.)

원안이 요구한 **"prefix로 완전 분리, 상호 무영향, `SCAN`으로 플랫폼별 모니터링"**
이라는 성질은 이 배치로도 그대로 만족한다.

```
authgw:refresh:{jti}                          ← 웹 (기존, String)
authgw:refresh:sessions:{sub}                 ← 웹 세션 인덱스 (기존, Set)
authgw:mobile:refresh:{sub}:{device_id}       ← 모바일 (신규, Hash)
authgw:mobile:sessions:{sub}                  ← 모바일 세션 인덱스 (신규, Set)
authgw:blacklist:{jti}                        ← access token 즉시 차단 (기존, 공용)
```

> 블랙리스트를 `auth:blacklist:mobile:{jti}` / `:web:{jti}`로 쪼개자는 원안은
> **채택하지 않는다.** `jti`는 UUID4라 플랫폼 간 충돌이 없고, 검증부
> (`core/dependencies.get_current_user`)는 토큰이 어느 플랫폼 것인지 모르는 채
> 조회하므로 쪼개면 매 요청 조회가 두 번이 된다. 플랫폼 구분이 필요하면
> §4.3의 `platform` 클레임을 쓴다.

### 2.2 모바일 세션 Hash 필드

```
HSET authgw:mobile:refresh:{sub}:{device_id}
  platform        "mobile"
  refresh_jti     <refresh token의 jti>
  refresh_hash    <refresh token 원문의 SHA-256 hex>
  device_id       <X-Device-Id 헤더 값>
  device_model    <optional, ex: "SM-N960N">
  kakao_id        <카카오 회원번호(문자열)> — sub의 근거
  email           <optional> 인증에 쓰지 않는다. 카카오가 안 주면 빈 값 (§6-Q1)
  issued_at       <ISO8601>
  expires_at      <ISO8601>
  last_active_at  <ISO8601>

EXPIRE authgw:mobile:refresh:{sub}:{device_id} <refresh TTL 초>
SADD   authgw:mobile:sessions:{sub} {device_id}
```

- **refresh token 원문을 저장하지 않는다.** SHA-256 hex(`refresh_hash`)만 저장하고
  대조도 해시값으로 한다 (원안 §5-2).
- TTL은 refresh token 만료 시각과 **같은 값**으로 `EXPIRE` — 모바일 30일 / 웹 14일
  (§6-Q2). 실기기 로그인 후 `TTL` 이 2,591,980초(≈30.0일)로 확인됐다.
- `authgw:mobile:sessions:{sub}` Set에는 TTL이 걸리지 않아 만료된 `device_id`가
  남는다 — 기기 목록 조회·`logout-all` 시 `EXISTS`로 걸러내고 `SREM`으로 청소한다.

### 2.3 모바일·웹 세션이 서로 무영향인 근거

- 키 prefix가 다르므로 `revoke`/`revoke_all`의 대상 키 집합이 겹치지 않는다.
- 단, 기존 `RefreshTokenStore.revoke_all(sub)`는 **웹 세션만** 지운다. 리프레시
  재사용 감지 시 모바일까지 끊을지는 정책 선택이다 → §6-Q3.

---

## 3. 엔드포인트 명세

`auth` 컨테이너(:9000) 기준. `auth_main.py`가 `/auth` prefix로 마운트한다.

| Method | 실제 경로 | 원안 표기 | 설명 |
|---|---|---|---|
| POST | `/auth/kakao/mobile` | `/api/v1/auth/kakao/mobile` | 모바일 카카오 로그인 → JWT 발급 |
| POST | `/auth/mobile/refresh` | 동일 | 모바일 refresh → access 재발급 (로테이션) |
| POST | `/auth/mobile/logout` | 동일 | 해당 `device_id` 세션만 삭제 |
| POST | `/auth/mobile/logout-all` | 동일 | 유저의 모바일 세션 전부 삭제 (웹 무영향) |
| POST | `/auth/kakao/web` | 동일 | **만들지 않는다** — 기존 `/auth/login` + `/auth/callback/kakao`가 이미 웹 흐름이다 |

> 원안 §6의 "웹 로그인 라우터는 스텁만 생성"은 **불필요**하다. 중복 흐름을 만들면
> 웹 세션 저장 경로가 둘로 갈라진다.

### 3.1 `POST /auth/kakao/mobile`

```
Header
  X-Device-Id: <device_id>          필수 — 없으면 400 (세션 키 구성 불가)
  X-Device-Model: <model>           선택

Body   { "access_token": "<카카오 access token>" }
  또는 { "id_token": "<카카오 OIDC id_token>" }        ※ 둘 중 하나 필수

200
  {
    "access_token": "<자체 access JWT>",
    "refresh_token": "<자체 refresh JWT>",
    "expires_in": 600,
    "token_type": "bearer"
  }
```

| 상태 | 조건 |
|---|---|
| 400 | `X-Device-Id` 누락 / body에 토큰 없음 |
| 401 | 카카오 토큰 검증 실패(만료·위조) |
| 502 | 카카오 API 응답 실패·타임아웃, 또는 응답에 회원번호가 없음 |
| 503 | 카카오 설정 누락(`OAuthNotConfiguredError`) |

> **403은 없다.** 초안에는 이메일 미동의 시 403이 있었지만, 이메일을 `sub`로 쓰지
> 않기로 하면서 사라졌다 — §6-Q1.

- 모바일은 **쿠키를 쓰지 않는다.** 토큰은 JSON 본문으로만 반환한다.
  `_set_token_cookies`는 웹 전용 — 모바일 경로에서 호출하지 말 것.

### 3.2 `POST /auth/mobile/refresh`

```
Header  X-Device-Id: <device_id>    필수
Body    { "refresh_token": "<자체 refresh JWT>" }
200     { "access_token": "...", "refresh_token": "<회전된 새 토큰>", "expires_in": 600 }
401     서명·만료 검증 실패 / 해시 불일치(재사용 의심) / 세션 없음
```

- 처리 순서: `verify_token(token, aud="refresh")` →
  `authgw:mobile:refresh:{sub}:{device_id}` 조회 → `refresh_hash` 대조 →
  새 쌍 발급 → Hash 갱신(`refresh_jti`·`refresh_hash`·`issued_at`·`expires_at`·
  `last_active_at`) + `EXPIRE` 재설정.
- 해시가 어긋나면 **탈취된 토큰의 재사용**이다. 최소한 해당 device 세션은 폐기한다
  (폐기 범위는 §6-Q3).

### 3.3 `POST /auth/mobile/logout` · `/auth/mobile/logout-all`

- `logout`: `DEL authgw:mobile:refresh:{sub}:{device_id}` + 인덱스 `SREM`.
- `logout-all`: `SMEMBERS authgw:mobile:sessions:{sub}` 순회 삭제 + Set 삭제.
  **`authgw:refresh:*`(웹)에는 손대지 않는다.**
- 남은 access token까지 즉시 죽여야 하면 `blacklist_access_token(jti, 남은 TTL)`.

---

## 4. 구현 배치

### 4.1 카카오 토큰 검증 (모바일/웹 공용)

[`core/matrix/kakao_oauth_client.py`](../core/matrix/kakao_oauth_client.py)에 함수를 **추가**한다.
기존 `build_authorize_url` / `exchange_code_for_tokens`는 웹 code 흐름 전용이고,
모바일은 **code 교환 단계가 아예 없다** — SDK가 이미 access token을 들고 있다.

```
async def verify_access_token(access_token: str) -> dict   # kapi.kakao.com/v2/user/me
async def verify_id_token(id_token: str) -> dict           # 카카오 JWKS로 로컬 서명 검증
```

둘 다 아래 형태로 **정규화**해 반환한다:

```
{"kakao_id": "3xxxxxxxxx", "email": "...", "name": "..."}
```

- 기존 `fetch_userinfo`는 `email`/`name`만 뽑고 **카카오 회원번호(`id`)를 버린다.**
  모바일 세션 Hash에 `kakao_id`가 필요하므로 신규 함수는 `body["id"]`를 포함한다.
  기존 함수의 반환 형태는 웹 콜백이 의존하므로 **바꾸지 않는다.**
- `id_token` 검증은 `https://kauth.kakao.com/.well-known/jwks.json`을 캐시하고
  `iss=https://kauth.kakao.com`, `aud=<앱 키>`를 확인한다(어느 키인지는 §6-Q4).
  **원격 호출이 없어 `access_token` 경로보다 빠르고 카카오 장애에 덜 묶인다.**
- 원안 §5-1대로 **검증 로직은 공용, 세션 저장만 플랫폼별 분기.**

### 4.2 모바일 세션 저장소

`apps/auth/services.py`에 `MobileSessionStore`를 추가한다.
기존 `RefreshTokenStore`는 **수정하지 않는다** (웹 회귀 위험).

```
class MobileSessionStore:
    async def register(sub, device_id, refresh_token, refresh_jti, ttl, kakao_id, device_model, email) -> None
    async def rotate(sub, device_id, old_refresh_token, new_refresh_token, new_refresh_jti, ttl) -> None
    async def revoke(sub, device_id) -> None
    async def revoke_all(sub) -> None
    async def list_devices(sub) -> list[dict]        # 선택 — 기기 목록 UI용
```

- `redis.asyncio` 사용, `REDIS_URL`에서 접속 (`RefreshTokenStore`와 동일 패턴).
- `Depends(get_mobile_session_store)` 싱글턴 — 매 요청 커넥션 재생성 금지
  (`get_refresh_store` 주석과 같은 이유). 테스트는 `dependency_overrides`로 교체.

### 4.3 라우터 분리

원안 §4 각주대로 **파일을 나눈다.**

```
apps/auth/
├── router.py            # 기존 웹 흐름 — 수정 없음
├── router_mobile.py     # 신규 — 모바일 4개 엔드포인트
├── services.py          # RefreshTokenStore(기존) + MobileSessionStore(신규)
└── schemas.py           # KakaoMobileLoginRequest, MobileTokenResponse 등 추가
```

`auth_main.py`에 한 줄 추가: `app.include_router(mobile_router, prefix="/auth")`.

access JWT에 `platform: "mobile" | "web"` 클레임을 넣을지 — **넣기를 권한다.**
`core.security.create_access_token`은 현재 `sub`/`roles`/`aud`/`iat`/`exp`/`jti`만
발급하므로 시그니처가 바뀐다. 이 함수는 웹 경로도 공유하므로 **기본값 있는 선택
인자**로 추가해 기존 호출부가 깨지지 않게 한다. → §6-Q5

### 4.4 importlinter

`auth-isolation` contract(`apps.auth`는 `auth_main`만 import)에 `router_mobile`이
새로 걸리지 않는지 `lint-imports`로 확인한다. `core.matrix.kakao_oauth_client`는
`core` 소속이라 계약 위반이 아니다.

---

## 5. 환경 변수

| 변수 | 위치 | 용도 | 현재 상태 |
|---|---|---|---|
| `REDIS_URL` | `.env.auth` | 세션 저장소 | 코드가 이미 읽음(기본 `redis://localhost:6379/0`). compose에서는 `redis://redis:6379/0` |
| `KAKAO_CLIENT_ID` | `.env.auth` | 웹 code 흐름 + `id_token`의 `aud` 검증 | 있음 |
| `KAKAO_CLIENT_SECRET` | `.env.auth` | 카카오 "Client Secret"을 켠 경우만 | 선택 |
| `KAKAO_REDIRECT_URI` | `.env.auth` | 웹 전용 | 있음. **모바일은 쓰지 않는다** |
| `KAKAO_NATIVE_APP_KEY` | `.env.auth` | 모바일 `id_token`의 `aud` 검증 | **없으면 `id_token` 경로가 꺼진다**(access_token 경로로 자동 폴백). Flutter의 `--dart-define=KAKAO_NATIVE_APP_KEY` 와 같은 값 |
| `JWT_PRIVATE_KEY` | `.env.auth` | 발급 (auth 컨테이너에만) | 있음 |
| `JWT_PUBLIC_KEY` | `.env.backend` | 검증 (전 컨테이너 공용) | 있음 |

`.env.*`는 커밋하지 않는다 (`auth-gateway-harness.md` §1 절대 규칙).

> **`REDIS_URL` 은 이미 설정돼 있다** — 2026-08-03 EC2의 `.env.auth` 에서
> `redis://redis:6379/0` 확인. compose의 `auth` 서비스는 `environment:` 로 Redis
> 주소를 주지 않고 `.env.auth` 만 읽으므로, 이 값이 없으면 코드 기본값
> `redis://localhost:6379/0` 이 쓰여 컨테이너 안에서 Redis를 못 찾는다.
> 배포 환경을 새로 만들 때 빠뜨리기 쉬운 항목이라 남겨 둔다.

---

## 6. 결정 사항과 남은 질문

착수 전 열어 뒀던 5개 중 4개는 코드로 정해졌다. 바꾸려면 아래 위치를 고친다.

| # | 결정 | 근거 · 위치 |
|---|---|---|
| Q2 | **모바일 30일 / 웹 14일** | `MOBILE_REFRESH_TOKEN_TTL_DAYS`. 토큰 `exp`와 Redis TTL이 같은 상수에서 나오도록 `issue_mobile_token_pair`가 함께 계산한다 |
| Q3 | 재사용 감지 시 **그 사용자의 모바일 세션 전체 폐기, 웹은 무영향** | 웹이 "웹 세션 전체 폐기"인 것과 대칭. `MobileSessionStore.rotate` |
| Q4 | **둘 다 구현.** `id_token`이 오고 서버에 `KAKAO_NATIVE_APP_KEY`가 있으면 로컬 검증, 아니면 `access_token` 원격 검증 | 콘솔에서 OIDC를 켜고 끌 때 앱을 다시 배포하지 않아도 된다. `router_mobile._verify_kakao` |
| Q5 | **넣는다** (`platform: "mobile"`) | `create_access_token(platform=...)`은 기본값 `None`인 선택 인자라 웹 발급부는 그대로다 |

### Q1 — 모바일 `sub`는 **카카오 회원번호**다 (2026-08-03 결정)

세션 키의 `{user_id}` 자리에 `kakao:{kakao_id}` 가 들어간다. 예:

```
authgw:mobile:refresh:kakao:5021010517:{device_id}
```

**이메일을 못 쓰는 이유:** 카카오는 이메일 수집을 **비즈니스 앱**(사업자등록번호 +
심사) 전환 이후로 제한한다. 개인 개발자 앱에서는 콘솔의 동의항목 →
개인정보 → `카카오계정(이메일)` 이 **"권한없음"** 으로 잠겨 있다(실기기 테스트 중 확인).
이메일을 `sub`로 쓰면 카카오가 빈 문자열을 주고, 로그인이 **403**으로 전부 막힌다.

**대가:** 웹 흐름(`router.py`)은 계속 이메일을 `sub`로 쓴다. 따라서 **같은 사람이
웹과 모바일에서 서로 다른 `sub`를 갖는다.** 지금은 두 플랫폼이 세션을 공유하지
않으므로 실질적 문제가 없지만, 한 사용자로 묶으려면 users 테이블에
`kakao_id ↔ email` 매핑이 필요하다.

**이관은 지금이 가장 싸다** — 모바일 세션은 오늘 처음 생겼고 users 테이블도
없다. 나중에 데이터가 쌓인 뒤 바꾸면 기존 세션·사용자 매핑을 손으로 옮겨야 한다.
이메일은 인증에 쓰지 않지만 세션 Hash의 `email` 필드에 남겨 두므로(받을 수 있을
때만 채워진다) 이관 근거로 쓸 수 있다.

---

## 7. 작업 순서

원안 §6에서 **이미 끝난 항목(Redis 추가)을 빼고** 이 저장소 구조에 맞게 재배열했다.

- [x] `core/matrix/kakao_oauth_client.py`에 `verify_access_token` / `verify_id_token` 추가
      (기존 함수 시그니처 무변경)
- [x] `apps/auth/schemas.py`에 모바일 요청·응답 스키마 추가
- [x] `apps/auth/services.py`에 `MobileSessionStore` + `get_mobile_session_store` 추가
- [x] `apps/auth/router_mobile.py` 신규 — 4개 엔드포인트
- [x] `auth_main.py`에 mobile 라우터 include
- [x] `core/security.py`에 선택 인자 `platform` (Q5)
- [x] `apps/auth/tests/test_router_mobile.py` — §8 테스트 21개
- [x] `lint-imports` 4개 계약 통과 + `pytest apps/auth/tests` 회귀 없음
- [ ] **`.env.auth` 에 `REDIS_URL` · `KAKAO_NATIVE_APP_KEY` 기입** (§5) — 저장소 밖 작업
- [ ] Q1 확정 (users 테이블로 갈지) — 지금은 이메일 `sub` 로 동작한다
- [ ] 실제 Redis·실제 카카오 토큰으로 종단 확인 — 테스트는 둘 다 더블을 쓴다

---

## 8. 완료 기준 (Acceptance Criteria)

`apps/auth/tests/test_router_mobile.py` 21개가 모두 이 목록에 대응한다.

- [x] `X-Device-Id` 없는 `/auth/kakao/mobile` 요청이 **400**
- [x] 위조·만료된 카카오 토큰이 **401** (카카오 API는 더블)
- [x] 이메일 동의 없음 **403**, 카카오 API 장애 **502**
- [x] 로그인 → refresh → logout 통과, 회전된 옛 refresh 재사용 시 **401**
- [x] **같은 계정의 웹 세션(`authgw:refresh:*`)이 있는 상태에서**
      `/auth/mobile/logout-all` 후 웹 세션 키가 **그대로 남아 있음**
      — 원안 §1의 핵심 요구사항. 이게 없으면 "분리"를 증명하지 못한다
- [x] 반대로 웹 `/auth/logout` 후 모바일 세션 Hash가 남아 있음
- [x] device_id A·B 동시 로그인 시 A의 logout이 B에 영향 없음
- [x] 재사용 감지가 **모바일 세션만** 전부 끊고 웹은 남김
- [x] Redis Hash에 refresh token **원문이 없음**(sha256 hex만 저장)
- [x] 모바일은 `Set-Cookie` 를 내지 않음
- [x] access token에 `platform="mobile"` 클레임이 실림
- [x] 기존 웹 인증 테스트 회귀 없음 — `pytest apps/auth/tests` 50 passed
      (1 failed는 이 작업 전부터 있던 `test_main_app_boots_...` — `main.py` 부팅에
      `neo4j_graphrag` 가 필요한 환경 문제)
- [x] `lint-imports` 4개 계약 KEPT (`apps.auth는 auth_main에서만 import된다` 포함)
- [ ] **실제 Redis·실제 카카오 토큰 종단 확인** — 위 전부 인메모리 더블 기준이다

---

## 9. 왜 플랫폼을 분리하는가

- 모바일과 웹은 **토큰 탈취 위험·세션 수명·디바이스 개념 자체가 다르다.** 만료와
  폐기 정책을 독립적으로 운영해야 한쪽 사고가 다른 쪽으로 번지지 않는다.
- key prefix 분리 덕분에 운영 중 `SCAN authgw:mobile:*` / `SCAN authgw:refresh:*` 로
  플랫폼별 세션 현황을 따로 관찰·디버깅할 수 있다.
- 추후 웹에 CSRF 토큰, 모바일에 FCM push token 같은 **플랫폼 고유 필드**를 붙일 때
  스키마 충돌 없이 확장된다.
- 저장 구조가 다른 이유도 여기 있다 — 웹은 브라우저가 쿠키를 관리하므로 `jti` 키로
  충분하지만, 모바일은 **기기 단위로 세션을 나열·폐기**해야 해서
  `{sub}:{device_id}` 복합키 + Hash가 필요하다.
