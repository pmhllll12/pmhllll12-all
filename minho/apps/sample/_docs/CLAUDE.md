---
type: hub
app: star_craft
links:
  - silicon_valley
  - titanic
  - kingsman
  - lion_king
  - sherlock_homes
  - harry_porter
  - jobs
---

# StarCraft 앱 — Hub

스타 토폴로지의 **중앙 허브**. 온톨로지 인덱스, 컨텍스트 라우팅, 앱 간 오케스트레이션을 담당한다.

---

## 캐릭터 체계

스타크래프트 캐릭터를 bounded context 식별자로 사용한다.

| 캐릭터 | 역할 |
|--------|------|
| `kerrigan` (Sarah Kerrigan) | 컨텍스트 라우터 — 쿼리를 분석해 적절한 스포크로 라우팅 |
| `raynor` (Jim Raynor) | 스포크 레지스트리 — 등록된 스포크 앱 목록 관리 |

---

## 헥사고날 레이어

```
apps/star_craft/
├── domain/
│   ├── spoke_registry.py       # SpokeApp 엔티티, SpokeStatus
│   └── routing_context.py      # RoutingContext 값 객체
├── app/
│   ├── dtos/
│   │   ├── kerrigan_context_router_dto.py   # ContextRouteCommand / Response
│   │   └── raynor_spoke_registry_dto.py     # SpokeListQuery / SpokeListResponse
│   ├── ports/input/
│   │   ├── kerrigan_context_router_use_case.py
│   │   └── raynor_spoke_registry_use_case.py
│   ├── ports/output/
│   │   ├── kerrigan_context_router_port.py
│   │   └── raynor_spoke_registry_port.py
│   └── use_cases/
│       ├── kerrigan_context_router_interactor.py
│       └── raynor_spoke_registry_interactor.py
├── adapter/
│   ├── inbound/
│   │   ├── api/
│   │   │   ├── __init__.py          # star_craft_router 노출
│   │   │   ├── schemas/             # Pydantic 요청·응답 모델
│   │   │   └── v1/                  # FastAPI 라우터 (/hub/route, /hub/spokes)
│   │   └── mcp/                     # MCP 툴 (route_to_spoke, list_spokes)
│   └── outbound/
│       ├── kerrigan_context_router_repository.py   # LLM 라우팅 placeholder
│       └── raynor_spoke_registry_repository.py     # 인메모리 스포크 레지스트리
├── dependencies/
│   └── providers.py
└── tests/
    ├── domain/
    │   └── test_spoke_registry_raynor_domain.py
    └── app/use_cases/
        ├── test_kerrigan_context_router_interactor.py
        └── test_raynor_spoke_registry_interactor.py
```

**의존성 방향:** `adapter` → `app` → `domain`

---

## API 엔드포인트

| Method | Path | 캐릭터 | 설명 |
|--------|------|--------|------|
| `POST` | `/api/hub/route` | kerrigan | 쿼리 → 스포크 라우팅 |
| `GET` | `/api/hub/spokes` | raynor | 등록된 스포크 목록 조회 |

---

## Hub 확장 규칙

새 스포크 앱이 추가되면:

1. `adapter/outbound/raynor_spoke_registry_repository.py`의 `_REGISTRY`에 항목 추가
2. `adapter/inbound/mcp/raynor_spoke_registry_tools.py`의 `_SPOKES` 리스트 업데이트
3. `scripts/validate_harness.py`의 `SPOKE_APPS` 집합에 앱 이름 추가
4. `fastapi/.importlinter`의 source/forbidden_modules에 앱 이름 추가
5. 이 문서의 frontmatter `links`에 앱 이름 추가

---

## TDD

```bash
cd tailor
python -m pytest apps/star_craft/tests/ -v
```
