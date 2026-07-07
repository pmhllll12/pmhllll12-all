# 스타 토폴로지 + 온톨로지 + 클린 아키텍처

`minho`는 모듈러 모놀리스다. 지금까지는 앱마다 독립적인 클린 아키텍처(도메인 →
유스케이스 → 어댑터)만 지켰고, 앱 간 관계는 "직접 import 금지"라는 느슨한 규칙
하나뿐이었다. 여기서는 그 관계에 **방향성**을 추가한다.

## 토폴로지

```
                         ┌──────────────┐
                         │  star_craft  │  ← 허브 (hub)
                         │ domain/app/  │     스포크를 알고 조율한다
                         │   adapter    │
                         └──────┬───────┘
              ┌──────────┬──────┼──────┬──────────┐
              ▼          ▼      ▼      ▼          ▼
          titanic   friday_13th  ...  soccer  social_network   ← 스포크 (spoke)
              │          │             │          │
              └──────────┴──────┬──────┴──────────┘
                                 ▼
                    core / matrix / adapters / ontology         ← 공통 기반
                    (허브·스포크 누구나 참조, 이들은 아무도 모름)
```

- **허브 → 스포크**: 허용. `star_craft`는 여러 스포크의 유스케이스를 조합해
  오케스트레이션한다 (예: 매칭 결과를 모아 알림을 보내는 흐름).
- **스포크 → 스포크**: 금지. 두 스포크가 협력해야 하면 허브를 거치거나, 공유할
  개념을 `ontology`로 끌어올린다.
- **(허브·스포크) → 공통 기반**: 허용. `core`, `matrix`, `apps/adapters`,
  `core/ontology`는 그래프 최하단이며 위쪽을 절대 모른다.
- **모듈 내부**: 기존 클린 아키텍처 그대로 — `adapter → app → domain` (바깥쪽이
  안쪽을 알고, 안쪽은 바깥쪽을 모른다).

## 온톨로지(ontology)란 무엇인가

스포크 간 직접 의존을 막으면, 두 스포크가 같은 개념(예: "탑승객"과 "선수"가 둘 다
참조하는 "사람")을 표현해야 할 때 문제가 생긴다. 이때 그 공유 개념의 **정의**(타입,
값 객체, enum, 매핑 규칙)를 `core/ontology/`에 두고, 양쪽 스포크가 거기서 가져다
쓴다. ontology는 특정 스포크의 구체적인 구현(ORM, 라우터 등)을 절대 모른다 —
순수한 타입/개념 정의만 둔다. 지금은 빈 패키지([`core/ontology/__init__.py`](../core/ontology/__init__.py))이고,
실제 공유 개념이 생길 때 채운다.

## 강제 방법: import-linter

ESLint의 `no-restricted-imports`/`dependency-cruiser`에 대응하는 Python 도구는
[`import-linter`](https://pypi.org/project/import-linter/)다. 규칙은
[`pyproject.toml`](../pyproject.toml)의 `[tool.importlinter]`에 있다.

| contract | 강제하는 규칙 |
|---|---|
| `forbidden` (허브→스포크 단방향) | 스포크가 `star_craft`를 import하면 실패 |
| `independence` (스포크 간) | 스포크끼리 서로 import하면 실패 |
| `forbidden` (공통 기반) | `core`/`matrix`/`adapters`/`ontology`가 허브·스포크를 import하면 실패 |
| `layers` (모듈 내부) | 각 앱 안에서 `domain`이 `app`/`adapter`를 import하면 실패, `app`이 `adapter`를 import하면 실패 |

**실행:**

```powershell
cd minho
pip install -r requirements-dev.txt
$env:PYTHONPATH = "$PWD;$PWD/apps;$PWD/core"   # main.py 의 sys.path 구성과 동일
lint-imports
ruff check .
ruff format --check .
```

**알려진 위반 (새 규칙 적용 전부터 존재):** `apps/friday_13th/app/bootstrap.py`가
`titanic.adapter.outbound.orm`을 직접 import한다. `independence` contract를 처음
돌리면 이 줄 때문에 실패한다 — 허브를 거치도록 고치거나, 공유 ORM 매핑을
`ontology`로 옮겨야 한다 (이 문서는 규칙만 강제하며, 기존 위반의 리팩터는 별도
작업).

**미포함 앱:** `soccer`, `matching`은 아직 `domain` 계층이 없어 `layers`
contract 대상에서 뺐다. `titanic`은 `app`(ports/use_cases)이 `adapter`의
schemas를 직접 import하는 기존 위반이 약 25곳 있어 마찬가지로 제외했다 — DTO를
`app/dtos/`로 옮기는 별도 작업 후 다시 넣는다. 계층을 갖추거나 정리하면
`pyproject.toml`의 `containers` 목록에 추가한다. `admin`은 아직 빈 패키지라
모든 contract에서 제외했다.

## CI / pre-commit

`minho`는 서브모듈(별도 저장소 `cloud.pmhllll12.api`)이라 CI·pre-commit 설정이
**여기 자체에** 있어야 실제로 동작한다 (저장소 루트의 `.github/`에 두면 minho 자신의
PR에서는 절대 실행되지 않는다 — 슈퍼프로젝트는 서브모듈 내부 파일 변경을 보지 못한다).

- `.github/workflows/architecture-check.yml` — push/PR마다 `lint-imports`, `ruff check`,
  `ruff format --check` 실행.
- `.pre-commit-config.yaml` — 로컬 커밋 전에 같은 3개를 실행 (설치: `pre-commit install`,
  `minho/` 안에서 실행).
- `scripts/check_architecture.sh` — `lint-imports`에 필요한 `PYTHONPATH`(backend root +
  apps + core, `main.py`의 sys.path 구성과 동일)를 매번 다시 안 적어도 되게 감싼 스크립트.

**mypy는 도입하지 않았다.** `main.py`가 런타임에 backend root·`apps/`·`core/` 세 곳을
동시에 `sys.path`에 넣는 구조라(`from titanic...`, `from matrix...`처럼 바로 top-level
import) mypy의 패키지 루트 추론과 충돌해 `Duplicate module named "__main__"` 류의
오류로 막힌다. sys.path 구조 자체를 손대지 않는 한 깨끗하게 넣기 어려워 보류했다.
