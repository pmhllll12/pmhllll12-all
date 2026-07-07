# 백엔드 (`minho`) — LLM 코딩 지침

FastAPI 백엔드 워크스페이스. 진입점은 [`main.py`](main.py) 이고, 도메인 코드는 [`apps/`](apps/) 아래 **시블링 앱**으로 둔다.

공통 4원칙 전문 ---> [`../_docs/CLAUDE.md`](../_docs/CLAUDE.md)  
에이전트 하네스 ---> [`../_docs/AGENTS.md`](../_docs/AGENTS.md)  
모노레포 지도 ---> [`../CLAUDE.md`](../CLAUDE.md)

---

## 디렉터리

| 경로 | 역할 |
|------|------|
| `main.py` | FastAPI 앱, `titanic_router` 등 마운트 |
| `apps/` | 도메인 패키지 (`titanic`, 추후 `soccer` …) |
| `core/` | `matrix` 등 공통 모듈 |
| `alembic/` | DB 마이그레이션 |
| `database.py` | SQLAlchemy 엔진·세션 |
| `.env` | `DATABASE_URL`, `GEMINI_API_KEY`, `API_PORT` 등 |
| `docker_entrypoint.py` | Docker: alembic(선택) + uvicorn |

---

## `apps/` 시블링 구조 — 스타 토폴로지 (허브/스포크)

```
minho/apps/
├── star_craft/       # 허브 — 스포크를 알고 조율. 스포크는 허브를 모름.
├── titanic/          # 스포크 — 타이타닉 데모 (헥사고날)
│   ├── .cursorrules
│   └── _docs/CLAUDE.md
└── <future-app>/     # 새 스포크는 같은 층에 추가
```

- **허브(`star_craft`) → 스포크**는 허용, **스포크 → 스포크**는 철저히 금지,
  **스포크 → 허브**도 금지(허브만 스포크를 안다). 공유할 개념·타입은
  `core/ontology/`로 끌어올린다 — 상세 ---> [`_docs/architecture-star-topology.md`](_docs/architecture-star-topology.md)
- 이 경계는 `pyproject.toml`(`[tool.importlinter]`)로 빌드 타임에 강제된다.
  각 앱 내부의 `domain → app → adapter` 클린 아키텍처 계층도 같은 설정으로 검사한다.
- 앱별 규칙은 **`minho/apps/<앱>/.cursorrules`** 와 **`_docs/CLAUDE.md`** 에 둔다.

타이타닉 상세 ---> [`apps/titanic/_docs/CLAUDE.md`](apps/titanic/_docs/CLAUDE.md)

---

## 실행

### 로컬

```powershell
cd minho
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

- 문서: `http://127.0.0.1:8000/docs`
- 헬스: `http://127.0.0.1:8000/ping`

### Docker (루트)

```powershell
cd ..
docker compose up --build -d
```

- 브라우저 UI: `http://localhost:3000` (gateway)
- API 직접: `http://localhost:8000` (compose 포트 매핑 시)

게이트웨이·Docker 오류 ---> [`../docker/README.md`](../docker/README.md)

---

## API 경로 (프록시와 맞출 것)

- `titanic_router` prefix는 **`/api/titanic`**.
- Vite `www/vite.config.ts` 프록시: `/api` → 백엔드 (URI 그대로 전달).
- 게이트웨이 `location ^~ /api/` → 백엔드 (URI 그대로 전달, strip 없음).
- 예: `POST /api/titanic/smith/chat`, `POST /api/titanic/james/upload`

---

## 백엔드 규약 (`_docs`)

| 주제 | 정본 |
|------|------|
| 엔티티·PK | [`_docs/entity-rules.md`](_docs/entity-rules.md) |
| Alembic | [`alembic/README.md`](alembic/README.md) |
| 스타 토폴로지(허브/스포크/온톨로지) | [`_docs/architecture-star-topology.md`](_docs/architecture-star-topology.md) |

---

## 환경 변수 (요약)

| 변수 | 용도 |
|------|------|
| `DATABASE_URL` | Neon/PostgreSQL |
| `GEMINI_API_KEY` | 스미스 채팅 등 Gemini |
| `API_HOST` | Docker: `0.0.0.0` |
| `API_PORT` | 기본 `8000` |
