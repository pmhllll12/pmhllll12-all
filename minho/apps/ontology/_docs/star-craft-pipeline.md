# star_craft 허브 — Graph DB · Vector DB 파이프라인 전략

허브(`star_craft`)가 스포크를 조율할 때 두 가지 외부 저장소를 추가로 사용한다.

- **Graph DB (Neo4j)** — 스포크 간 *관계* 데이터(사용자↔사용자, 사용자↔콘텐츠 등)
- **Vector DB (Qdrant)** — 임베딩 기반 *시맨틱 검색* (유사 사용자, 콘텐츠 추천 등)

---

## 1. 전체 파이프라인 흐름

```
인바운드 요청
    │
    ▼
star_craft Hub (orchestrator use case)
    │
    ├─── [1] Qdrant 검색          ← 임베딩 유사도로 컨텍스트 후보 추출
    │         (vector outbound adapter)
    │
    ├─── [2] Neo4j 조회           ← 관계 그래프로 연관 노드 탐색
    │         (graph outbound adapter)
    │
    ├─── [3] 스포크 UseCase 호출  ← 위 컨텍스트를 인자로 전달
    │         (titanic / soccer / social_network …)
    │
    └─── [4] 결과 통합 → 응답
```

---

## 2. Docker 서비스 추가

`docker-compose.yaml` 루트에 아래 두 서비스를 추가한다.

```yaml
services:
  # --- 기존 서비스(backend / frontend / gateway / n8n) 생략 ---

  neo4j:
    image: neo4j:5-community
    ports:
      - "7474:7474"   # Browser UI
      - "7687:7687"   # Bolt (Python driver)
    environment:
      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}
    volumes:
      - neo4j_data:/data
    restart: always

  qdrant:
    image: qdrant/qdrant:v1.13.6
    ports:
      - "6333:6333"   # REST API
      - "6334:6334"   # gRPC
    volumes:
      - qdrant_data:/qdrant/storage
    restart: always

volumes:
  n8n_data:
  neo4j_data:
  qdrant_data:
```

| 서비스 | 브라우저 확인 URL | 용도 |
|--------|------------------|------|
| Neo4j  | `http://localhost:7474` | 그래프 탐색 UI (Neo4j Browser) |
| Qdrant | `http://localhost:6333/dashboard` | 컬렉션·벡터 상태 확인 |

---

## 3. 환경 변수

`minho/.env` 에 추가한다.

```dotenv
# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

Docker Compose 환경(컨테이너 내부)에서는 `localhost` 대신 서비스명을 쓴다.

```dotenv
NEO4J_URI=bolt://neo4j:7687
QDRANT_HOST=qdrant
```

---

## 4. Python 패키지

`minho/requirements.txt` 에 추가한다.

```text
neo4j==5.29.1          # 공식 비동기 드라이버 포함
qdrant-client==1.14.2  # 비동기 클라이언트 포함
```

---

## 5. star_craft 내부 파일 구조

```
minho/apps/star_craft/
├── domain/
│   └── __init__.py
├── app/
│   ├── ports/
│   │   └── output/
│   │       ├── graph_port.py          # Neo4j 아웃바운드 포트(인터페이스)
│   │       └── vector_port.py         # Qdrant 아웃바운드 포트(인터페이스)
│   └── use_cases/
│       └── hub_orchestrator.py        # 허브 오케스트레이터
├── adapter/
│   └── outbound/
│       ├── neo4j_graph_adapter.py     # Neo4j 실구현
│       └── qdrant_vector_adapter.py   # Qdrant 실구현
└── dependencies/
    └── providers.py                   # FastAPI Depends 팩토리
```

---

## 6. 어댑터 구현 패턴

### 6-1. Neo4j (그래프 어댑터)

```python
# adapter/outbound/neo4j_graph_adapter.py
from neo4j import AsyncGraphDatabase

class Neo4jGraphAdapter:
    def __init__(self, uri: str, user: str, password: str) -> None:
        self._driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def close(self) -> None:
        await self._driver.close()

    async def find_related_nodes(self, node_id: str, depth: int = 2) -> list[dict]:
        async with self._driver.session() as session:
            result = await session.run(
                "MATCH (n {id: $id})-[*1..$depth]-(m) RETURN m",
                id=node_id, depth=depth,
            )
            return [record["m"] async for record in result]
```

### 6-2. Qdrant (벡터 어댑터)

```python
# adapter/outbound/qdrant_vector_adapter.py
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import PointStruct

class QdrantVectorAdapter:
    def __init__(self, host: str, port: int) -> None:
        self._client = AsyncQdrantClient(host=host, port=port)

    async def search(
        self, collection: str, vector: list[float], top_k: int = 5
    ) -> list[dict]:
        results = await self._client.search(
            collection_name=collection,
            query_vector=vector,
            limit=top_k,
        )
        return [{"id": r.id, "score": r.score, "payload": r.payload} for r in results]

    async def upsert(
        self, collection: str, point_id: str, vector: list[float], payload: dict
    ) -> None:
        await self._client.upsert(
            collection_name=collection,
            points=[PointStruct(id=point_id, vector=vector, payload=payload)],
        )
```

### 6-3. 허브 오케스트레이터 사용 예시

```python
# app/use_cases/hub_orchestrator.py
class HubOrchestrator:
    def __init__(self, graph, vector, spoke_a, spoke_b) -> None:
        self.graph = graph
        self.vector = vector
        self.spoke_a = spoke_a
        self.spoke_b = spoke_b

    async def orchestrate(self, query: str, user_id: str) -> dict:
        # 1. 임베딩 생성 (EXAONE 또는 별도 임베딩 모델)
        embedding = await self._embed(query)

        # 2. Vector DB: 유사 컨텍스트 검색
        context = await self.vector.search("profiles", embedding, top_k=3)

        # 3. Graph DB: 관계 노드 탐색
        related = await self.graph.find_related_nodes(user_id, depth=2)

        # 4. 스포크 유스케이스 호출 (컨텍스트 전달)
        result_a = await self.spoke_a.run(query=query, context=context)
        result_b = await self.spoke_b.run(related_nodes=related)

        return {"context": context, "related": related, "results": [result_a, result_b]}
```

---

## 7. FastAPI lifespan 연동

Neo4j 드라이버는 앱 시작 시 생성하고 종료 시 닫아야 한다.
`main.py`의 `lifespan` 컨텍스트 매니저에 아래 패턴을 추가한다.

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... 기존 초기화 ...
    neo4j_adapter = Neo4jGraphAdapter(
        uri=os.getenv("NEO4J_URI"),
        user=os.getenv("NEO4J_USER"),
        password=os.getenv("NEO4J_PASSWORD"),
    )
    app.state.neo4j = neo4j_adapter
    try:
        yield
    finally:
        await neo4j_adapter.close()
        await dispose_engine()
```

---

## 8. 구현 순서 (권장)

| 단계 | 작업 |
|------|------|
| 1 | `docker-compose.yaml`에 Neo4j·Qdrant 추가 후 `docker compose up` |
| 2 | `requirements.txt`에 드라이버 추가 후 `pip install -r requirements.txt` |
| 3 | `.env`에 연결 변수 추가 |
| 4 | `graph_port.py`, `vector_port.py` 인터페이스 정의 |
| 5 | `neo4j_graph_adapter.py`, `qdrant_vector_adapter.py` 실구현 |
| 6 | `hub_orchestrator.py` 유스케이스 작성 |
| 7 | `providers.py`에 FastAPI Depends 팩토리 등록 |
| 8 | `main.py` lifespan에 Neo4j 드라이버 수명 관리 추가 |

---

## 9. 경계 규칙 재확인

이 파이프라인은 기존 스타 토폴로지 규칙을 그대로 따른다.

- Neo4j·Qdrant 어댑터는 **star_craft 내부 outbound 어댑터**에만 둔다.
- 스포크(`titanic`, `soccer` 등)는 graph/vector DB를 **직접 참조하지 않는다**.
- 스포크가 그래프·벡터 컨텍스트를 필요로 하면, 허브가 조회 후 DTO/ontology 타입으로 변환해서 전달한다.
- 공유 타입(예: `RelatedNode`, `SimilarProfile`)이 생기면 `core/ontology/`로 끌어올린다.
