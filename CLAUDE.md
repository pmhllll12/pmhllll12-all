# LLM 코딩 행동 지침 (모노레포 루트)

이 파일은 **저장소 전체**에서 Cursor·에이전트가 읽는 **진입점**이다.

**트레이드오프:** 속도보다 신중함. 사소한 작업은 상황에 맞게 판단한다.

---

## CLAUDE.md 계층

코드 작성 전 [`minho/CLAUDE.md`](minho/CLAUDE.md) 를 읽는다.

---

## 문서 배치 규칙 (`_docs`)

모든 비코드 규칙·가이드 MD는 내용의 범위에 따라 아래 4곳 중 하나에 둔다. 새 문서를 추가할 때도 이 표를 기준으로 위치를 정한다.

| 내용 범위 | 위치 | 예 |
|-----------|------|------|
| 공통(전 영역 공통 원칙·하네스) | [`_docs/`](_docs/) | `_docs/CLAUDE.md`, `_docs/AGENTS.md`, `_docs/DEV_SERVER.md` |
| 백엔드(`minho`) 전용 | [`minho/_docs/`](minho/_docs/) | `minho/_docs/entity-rules.md`, `auth-rules.md` 등 |
| 프런트엔드(`www`) 전용 | [`www/_docs/`](www/_docs/) | `www/_docs/react_rules.md`, `darkmode-spec.md` |
| 플러터(`pmh_flutter`) 전용 | [`pmh_flutter/_docs/`](pmh_flutter/_docs/) | (앱 추가 시 생성) |

- `minho/apps/<앱>/_docs/`(예: `titanic`)처럼 **앱 단위로 더 좁은 범위**가 필요하면 해당 앱 폴더 하위에 별도 `_docs/`를 둔다 — 위 표보다 우선한다.
- 과거 `vault/` 서브모듈에 두던 공통·영역별 문서는 모두 위 구조로 이전했다. 새 문서를 `vault/`에 추가하지 않는다.

---

## 빠른 실행

- API 문서: `http://localhost:8000/docs` (백엔드 기동 후)
- UI: `http://localhost:3000` (`docker compose` 또는 `www` 에서 `npm run dev`)
- 백엔드 로컬: [`minho/CLAUDE.md`](minho/CLAUDE.md)

# com.ragwatson

이 저장소는 **코드와 함께 두는 에이전트 하네스**(규칙·검증·스코프)를 전제로 한다. [Andrej Karpathy가 정리한 LLM 코딩 함정](https://x.com/karpathy/status/2015883857489522876)(침묵 가정, 과설계, diff 범람, 모호한 완료)을 줄이기 위해, 사람과 Cursor 에이전트가 같은 기준을 보도록 문서를 나눠 두었다.

**트레이드오프:** 속도보다 신중함. 사소한 변경은 판단으로 완화한다.

---

## 저장소 구조(요지)

- **루트의 하네스 문서:** 아래 “하네스 문서” 절 참고.
- **`agora/` 등:** 애플리케이션·실험 코드. 하위 프로젝트별 README·설정이 있으면 그쪽을 따른다.

루트에 단일 빌드 스크립트가 없을 수 있다. 실행·설치는 각 하위 프로젝트 문서를 본다.

---

## 하네스 문서(읽는 순서 권장)

1. [`CLAUDE.md`](CLAUDE.md) — **정본.** 네 원칙 전문·예시·`단계 → 검증` 템플릿. 프로젝트별 지침과 **병합**해 해석한다.
2. [`.cursorrules`](.cursorrules) — Cursor에 **항시** 주입되는 짧은 제약(경계·diff·완료 조건).
3. [`CURSOR.md`](CURSOR.md) — Cursor에서의 **운영 규약**(@ 컨텍스트, 프롬프트 설계, `.cursor/rules` 주의).
4. [`_docs/HARNESS-TOOLING.md`](_docs/HARNESS-TOOLING.md) — 위 원칙을 실제로 강제하는 린터·포매터·pre-commit·CI가 **어디에** 있는지(서브모듈 경계 주의).

원칙을 바꾸지 않는 한, 세 문서는 서로 **역할만** 나누고 같은 뜻을 유지한다.

---

## 카파시 의도 요약(기여·에이전트 공통)

1. **구현 전 사고** — 가정을 말로 밝히고, 불명확하면 질문한다. 해석이 여러 개면 몰래 고르지 않는다.
2. **단순성** — 요청 밖 기능·추상화·설정을 넣지 않는다.
3. **정밀한 수정** — 요청과 무관한 포맷·리팩터를 하지 않는다. diff의 각 줄이 요청과 연결되어야 한다.
4. **목표 중심** — “됐다” 대신 검증 가능한 완료 조건(테스트·빌드·재현 단계 등)을 먼저 둔다.

상세와 문장 수준의 지침은 반드시 [`CLAUDE.md`](CLAUDE.md)를 본다.

---

## 이 README의 역할

프로젝트 기능 설명이 길어지면 README가 또 하나의 “거대한 하네스”가 되어 모델과 사람 모두 핵심을 놓친다. **제품·도메인 상세**는 하위 패키지 README나 위키로 두고, 루트 README는 **입구 + 하네스 안내**에 집중한다.
