# 타이타닉 앱 (`minho/apps/titanic`) — LLM 코딩 지침

`minho/apps/` 아래 **시블링 도메인 앱**의 참조 구현. 새 앱 추가 시 같은 패턴을 따른다:

```
minho/apps/<앱명>/
├── .cursorrules
├── _docs/CLAUDE.md
├── adapter/
├── app/
├── domain/
└── dependencies/
```

백엔드 공통 ---> [`../../../CLAUDE.md`](../../../CLAUDE.md)  
ERD ---> [`../../../../vault/DevOps/Backend/TITANIC_ERD.md`](../../../../vault/DevOps/Backend/TITANIC_ERD.md)  
엔티티 규칙 ---> [`../../../../vault/DevOps/Backend/ENTITY_RULE.md`](../../../../vault/DevOps/Backend/ENTITY_RULE.md)

(`minho/apps/titanic/_docs` → 저장소 루트 `vault/` 는 `../../../../vault/`)

---

## 라우터 등록

[`adapter/inbound/api/__init__.py`](../adapter/inbound/api/__init__.py):

```python
titanic_router = APIRouter(prefix="/titanic", tags=["titanic"])
```

`main.py`에서 `app.include_router(titanic_router)` — **prefix 중복 금지**.

### 주요 엔드포인트 (예)

| 경로 | 설명 |
|------|------|
| `GET /titanic/` | API 인덱스 |
| `GET /titanic/james/myself` | 제임스 감독 |
| `POST /titanic/james/upload` | CSV 업로드 |
| `GET /titanic/rose/myself` | 로즈 |
| `POST /titanic/smith/chat` | 스미스 선장 채팅 (`GEMINI_API_KEY`) |

프론트: [`../../../../www/src/pages/TitanicSmith.tsx`](../../../../www/src/pages/TitanicSmith.tsx) → `POST /titanic/smith/chat` + `{"message":"..."}`.

---

## 캐릭터 모듈 (V1 라우터)

`adapter/inbound/api/V1/` — 파일명 패턴 `crew_*_router.py`, `passenger_*_router.py`.

각 라우터는 `APIRouter(prefix="/<캐릭터>", …)` 이고, 상위 `titanic_router`와 합쳐져 `/titanic/<캐릭터>/...` 가 된다.

---

## 유스케이스·의존성

- Provider: `dependencies/*_provider.py` — FastAPI `Depends(get_db)`.
- Interactor: `app/use_cases/*_interactor.py` — 포트(input/output) 구현.
- **스미스 선장**은 `JackTrainerUseCase`, `RoseModelUseCase` 를 생성자 주입으로 연결 가능 (`crew_smith_captin_interactor.py`).

스키마 이름은 라우터·포트·interactor에서 **동일**하게 유지:

- `SmithCaptainSchema`, `SmithChatRequest`, `SmithChatResponse` → `schemas/crew_smith_captin_schemas.py`

---

## ORM·DB

| 테이블 | ORM (예) | 비고 |
|--------|----------|------|
| James 로컬 업로드 | `persons`, `bookings` | `PersonOrm`, `BookingOrm` |
| Neon 레거시 | `titanic_persons`, `titanic_bookings` | `JamesPersonOrm`, `JamesBookingOrm` / `RoseModelOrm` |
| 승객 PK 예시 | `passengers` | `JackTrainerOrm` |

- `titanic_bookings` PK: **`passenger_id`** (마이그레이션 `20260521_0003`).
- Alembic ---> [`../../../alembic/README.md`](../../../alembic/README.md)

---

## 테스트

[`tests/`](../tests/) — `conftest.py` 에 앱·DB 픽스처를 두고 pytest 확장 예정.

---

## README (레거시 맵)

구 파일명 매핑 ---> [`../README.md`](../README.md)

## async 규칙

| 메소드 성격 | 형태 | 근거 |
|------------|------|------|
| CPU-bound (Kiwi 등 연산) | `def` | `async`를 붙여도 이벤트 루프 블로킹은 동일 |
| I/O-bound (DB·LLM·네트워크) | `async def` | `await` 가능한 호출이 있을 때만 |

Kiwi 처리가 무거워 이벤트 루프 블로킹이 문제가 된다면, `async def`로 바꾸는 대신 **호출 측**에서 스레드풀에 위임한다:

```python
result = await asyncio.to_thread(use_case.analyze_intent, question)
```

---

## 타이타닉 도메인 문서 연결

*타이타닉 도메인 문서연결
*타이타닉 피처 정리 : [[titanic-features]]
*타이타닉 머신러닝 : [[titanic-machine-learning]]
*타이타닉 ERD : [[titanic-erd]]
*타이타닉 알고리즘 : [[titanic-algorithm]]
*타이타닉 NF : [[titanic-nf]]



