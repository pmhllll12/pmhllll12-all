---
type: spoke
app: silicon_valley
links:
  - star_craft
---

# LangGraph 전략 — 문서 지식 그래프(GraphRAG)

단순 청크 검색을 넘어 **데이터 간 관계를 활용한 복합 추론(GraphRAG)** 과 **상태 기반
에이전트 워크플로우(LangGraph)** 를 `apps/admin`에 도입한다. 대상 유스케이스는
`document_graph` — 업로드된 PDF에서 엔티티·관계를 추출해 Neo4j에 적재하고, 벡터 검색과
그래프 탐색을 함께 써서 질의응답한다.

레이어 배치·명명·연결 규칙은 [002-neo4j-harness.md](002-neo4j-harness.md),
[003-langchain_harness.md](003-langchain_harness.md),
[004-langgraph_harness.md](004-langgraph_harness.md)를 그대로 따른다 — 이 문서는 그 규칙을
`document_graph` 유스케이스에 매핑한 것이며, 규칙 자체를 다시 서술하지 않는다.

---

## 0. 컨텍스트 — 이것은 "전환"이 아니라 "신규 구축"이다

이 전략은 흔히 "기존 LangChain + pgvector에서 LangGraph + Neo4j로 **전환**"으로 서술되지만,
`apps/admin` 기준으로는 사실과 다르다. 구현 전에 아래를 전제로 삼는다.

- **`apps/admin`에는 pgvector 기반 RAG가 없다.** 벡터 스토어·임베딩 호출·리트리버가 하나도
  없고, `domain/document_vector.py`는 **0바이트 빈 스텁**이다. 즉 **마이그레이션할 벡터
  데이터가 존재하지 않는다** — "pgvector에서 데이터를 옮긴다"는 단계는 이 앱에 없다.
- pgvector를 실제로 쓰는 곳은 **다른 스포크**다 — `community`(수신 메일),
  `moneyball`(선수), `ontology`(비전 분석). **이들은 이 전략의 이관 대상이 아니다.**
  스포크 간 참조는 금지돼 있고([`architecture-star-topology.md`](../../../_docs/architecture-star-topology.md)),
  각자의 pgvector 자산은 그대로 둔다.
- **`apps/admin`에서 LangChain은 실제로 import되지 않는다.** `langchain_chat_*`은 이름만
  LangChain이고 구현체는 `adapter/outbound/client/gemini_chat_client.py`(raw google-genai)다.
- **`langgraph==1.2.6`은 설치돼 있으나 저장소 어디서도 import되지 않는다.**
  [004-langgraph_harness.md](004-langgraph_harness.md) §0이 언급한
  `app/use_cases/langgraph_interactor.py` 스텁은 **현재 존재하지 않는다**(004의 낡은 서술은
  이 문서를 쓰면서 함께 정정했다).
- Neo4j 컨테이너는 `docker-compose.yaml`에 있지만 `backend.environment`에 `NEO4J_URI`가
  아직 주입되지 않았다([002-neo4j-harness.md](002-neo4j-harness.md) §4 미완). 이 전략의
  **첫 번째 선행 작업**이다.
- `apps/admin`에서 Neo4j를 쓰는 유일한 코드는
  `adapter/outbound/neo4j_graphrag_pdf_text_extractor.py`인데, 이것은 **Neo4j에 접속하지
  않는다** — `neo4j-graphrag` 패키지의 `PdfLoader`(pypdf 래퍼)만 빌려 쓸 뿐이다. 그래프 DB
  연결은 이 전략에서 처음 생긴다.

**따라서 이 문서는 "기존 자산의 이관 계획"이 아니라 "admin에 GraphRAG를 처음 짓는
설계"다.** pgvector를 새로 깔지 않고 Neo4j로 바로 가는 이유는 아래에 남긴다.

### 왜 pgvector를 건너뛰고 Neo4j로 가는가

옮길 데이터가 없다는 것은 곧 **선택이 자유롭다**는 뜻이다. 두 저장소를 모두 새로 만들어야
한다면, 아래 조건일 때만 Neo4j가 정당하다.

| 조건 | pgvector로 충분 | Neo4j 필요 |
|---|---|---|
| 질문이 "이 문서에 X에 대해 뭐라고 쓰여 있나?" 수준 | 유사도 검색 한 번이면 끝 | 과설계 |
| 질문이 "A와 B를 잇는 경로", "C에 2단계 이내로 연결된 것 전부" | 청크 유사도로는 표현 불가 | 그래프 탐색이 필요 |
| 여러 문서에 흩어진 사실을 관계로 이어 붙여야 함 | 표현 불가 | 그래프 탐색이 필요 |

**오른쪽 조건이 실제 요구로 확인되기 전에는 이 전략을 착수하지 않는다.** 왼쪽이면
[003-langchain_harness.md](003-langchain_harness.md)의 LCEL 체인 + 기존 pgvector 관례로
충분하며, 그편이 인프라도 의존성도 적다(루트 [CLAUDE.md](../../../../CLAUDE.md) 4원칙 —
과설계 금지).

---

## 1. 4단계 전략의 저장소 매핑

| 단계 | 전략 | 이 저장소의 구현 지점 |
|---|---|---|
| 1 | 그래프 적재 | 추출된 PDF 텍스트 → 청크 + 엔티티/관계 → Neo4j (벡터 인덱스 + 지식 그래프) |
| 2 | 하이브리드 검색 | 벡터 유사도 검색 + Text2Cypher 그래프 탐색을 조합 |
| 3 | 에이전트 워크플로우 | `StateGraph`로 라우터 → 검색 → 생성 흐름 구성 |
| 4 | 영속성 | 멀티턴 대화가 요구로 확인될 때만 Checkpointer 도입 (§5) |

---

## 2. 1단계 — 그래프 적재

기존 `pdf_loader` 스포크(`Neo4jGraphRagPdfTextExtractor` → `admin_pdf_summaries`)를 재사용한다.
PDF 파싱 파이프라인을 중복 구현하지 않는다([003-langchain_harness.md](003-langchain_harness.md) §0).

```
PDF 업로드 → (기존) 텍스트 추출 → 청크 분할 ┬→ 임베딩 → Neo4j 벡터 인덱스
                                          └→ 엔티티/관계 추출 → Neo4j 노드/관계
```

### 임베딩 차원은 이미 고정돼 있다

`core/matrix/vault_keymaker_secret_manager.py`의 `keymaker.embed_content`는
`gemini-embedding-001`을 **`output_dimensionality=768`로 잘라서** 반환한다(`EMBEDDING_DIM = 768`).

- **Neo4j 벡터 인덱스도 반드시 `768` 차원 + `cosine` 유사도로 생성한다.** 모델 기본값
  (3072)으로 만들면 적재 시점에 조용히 깨진다.
- 차원 상수는 새로 정의하지 말고 `core.matrix.vault_keymaker_secret_manager.EMBEDDING_DIM`을
  import해서 쓴다 — 두 곳에 숫자를 적으면 갈라진다.

```cypher
CREATE VECTOR INDEX document_chunk_embedding IF NOT EXISTS
FOR (c:DocumentChunk) ON (c.embedding)
OPTIONS { indexConfig: {
  `vector.dimensions`: 768,
  `vector.similarity_function`: 'cosine'
} };
```

이 인덱스 생성 Cypher는 코드에 하드코딩하지 않고
[002-neo4j-harness.md](002-neo4j-harness.md) §5대로 `graph_migrations/`에 idempotent 스크립트로
둔다.

### 엔티티/관계 추출

`LLMGraphTransformer` 같은 헬퍼로 텍스트에서 노드·관계를 뽑는다. 단, 아래를 지킨다.

- **추출할 라벨·관계 타입을 미리 화이트리스트로 고정한다.** LLM이 자유롭게 라벨을 만들게
  두면 `Person`/`person`/`PERSON`이 뒤섞여 그래프가 며칠 만에 못 쓰게 된다.
  [002-neo4j-harness.md](002-neo4j-harness.md) §2의 표기 규칙(라벨 PascalCase 단수,
  관계 SCREAMING_SNAKE_CASE, 속성 snake_case)을 추출기 설정에 그대로 강제한다.
- 노드 병합은 `MERGE (n:Label {id: $id})` — 식별자 속성으로만 매칭한다(002 §5).
- 원본 청크 노드(`:DocumentChunk`)와 추출된 엔티티를 관계로 이어 **출처를 추적 가능하게**
  둔다(예: `(:DocumentChunk)-[:MENTIONS]->(:Entity)`). 이게 있어야 2단계 하이브리드 검색에서
  그래프 탐색 결과를 원문으로 되짚을 수 있다.

---

## 3. 2단계 — 하이브리드 검색

### 두 경로

- **벡터 경로**: 질문 임베딩 → `db.index.vector.queryNodes`로 유사 청크 top-k 조회.
- **그래프 경로**: 질문 → LLM이 Cypher 생성(Text2Cypher) → 실행 → 구조화된 결과.

두 결과를 합쳐 프롬프트 컨텍스트로 넘긴다. **어느 경로에서 왔는지 라벨을 붙여서** 넘긴다 —
생성 단계에서 출처를 구분하지 못하면 환각을 줄이려던 목적이 사라진다.

### Text2Cypher 안전 규칙 (필수)

LLM이 만든 Cypher를 그대로 실행하는 것은 [002-neo4j-harness.md](002-neo4j-harness.md) §3의
"f-string으로 값을 쿼리에 삽입하지 않는다"와 **같은 계열의 위험**이다. 파라미터 바인딩으로
막을 수 있는 문제가 아니라 쿼리 전체가 LLM 출력이므로, 실행 측에서 막는다.

- **읽기 전용 세션으로만 실행한다** — `session.execute_read(...)`. 쓰기 트랜잭션 경로로
  LLM 생성 쿼리를 보내지 않는다.
- **쓰기·스키마 변경 키워드를 거부한다** — `CREATE`, `MERGE`, `DELETE`, `SET`, `REMOVE`,
  `DROP`, `LOAD CSV`, `CALL apoc.*` 등을 사전 검사로 걸러 낸다. 통과 실패 시 실행하지 않고
  벡터 경로 결과만으로 답한다(요청 전체를 실패시키지 않는다).
- **결과 행 수·실행 시간 상한을 건다** — 생성된 쿼리에 `LIMIT`이 없으면 강제로 붙이고,
  드라이버 레벨 타임아웃을 설정한다. 카티전 곱 한 번이 DB를 잡아먹는다.
- **`GraphCypherQAChain`의 `allow_dangerous_requests`를 무비판적으로 켜지 않는다.** 이 플래그는
  "위 보호 장치를 네가 직접 갖췄다"는 선언이다 — 위 세 항목을 구현한 뒤에만 켠다.
- 운영에서는 **읽기 전용 Neo4j 사용자**를 따로 만들어 Text2Cypher 경로에만 그 자격증명을
  쓰는 것을 권장한다(애플리케이션 레벨 검사의 이중 방어).

---

## 4. 3단계 — LangGraph StateGraph

[004-langgraph_harness.md](004-langgraph_harness.md) §2의 오른쪽 조건에 해당한다 — 질문에 따라
벡터 경로/그래프 경로/둘 다를 갈라야 하고, 생성된 Cypher가 무효면 재생성해야 한다. 그래서
단순 LCEL 체인이 아니라 `StateGraph`로 구성한다.

```
State: { question, route, vector_hits, cypher, cypher_is_valid, graph_rows, retry_count, answer }

[라우터 노드] → (조건부 엣지: route)
  ├─ "vector" → [벡터 검색 노드] ─────────────────┐
  ├─ "graph"  → [Cypher 생성 노드] → (조건부: cypher_is_valid?)
  │                 ├─ 유효 → [그래프 실행 노드] ──┤
  │                 └─ 무효 → [Cypher 생성 노드]로 되돌아감 (재시도 상한)
  └─ "hybrid" → [벡터 검색] + [Cypher 생성 → 실행] ┤
                                                   ↓
                                           [생성 노드] → END
```

- **재시도 상한은 필수다.** `retry_count`를 State에 두고 상한 초과 시 그래프 경로를 포기하고
  벡터 결과만으로 답한다 — 무한 루프 금지([007](007-langchain-elastic-strategy.md) §2와 동일).
- 각 노드는 어댑터(포트 구현체)를 호출하는 **얇은 wrapper**다. 노드 안에서 LangChain 체인을
  즉석 조립하지 않는다(004 §3).
- `graph.compile()`은 모듈 로드 시 한 번만 한다(004 §3).
- 노드 이름·State 키는 영어 snake_case(002 §2).

---

## 5. 4단계 — 영속성(Checkpointer)

### 도입 조건

[004-langgraph_harness.md](004-langgraph_harness.md) §1은 "Checkpointer는 실제 요구가 확인되기
전에는 도입하지 않는다(YAGNI)"고 정했다. 이 전략은 그 조건이 **충족될 때만** 예외를 연다.

**도입 조건**: 문서 질의응답이 멀티턴이 되어 이전 턴의 검색 컨텍스트를 다음 턴에서
이어 써야 하고, 그 세션이 프로세스 재시작을 넘어 유지되어야 할 때.

**단일 질의응답(질문 하나 → 답변 하나)이면 Checkpointer를 붙이지 않는다.** 현재 admin의
`langchain_chat` 유스케이스가 그렇다 — 상태를 저장할 이유가 없다.

### 저장소 선택 — Postgres 우선

조건이 충족되면 **`langgraph-checkpoint-postgres`(기존 Postgres 재사용)를 1순위로 쓴다.**

- 이 저장소에는 Postgres(pgvector 컨테이너)와 Redis가 **이미 떠 있다.** 체크포인터 하나
  때문에 새 인프라를 붙이지 않는다는 원칙([003](003-langchain_harness.md) §2)에 맞고,
  LangGraph 공식 패키지라 버전 호환·유지보수 경로가 분명하다.
- "에이전트 상태까지 Neo4j에 통합"은 개념적으로 깔끔해 보이지만, 체크포인트 데이터는
  **관계형 탐색 대상이 아니라 append-only 로그**다. 그래프 DB에 둘 실익이 크지 않다.

> **`Neo4jSaver` / `AsyncNeo4jSaver` 관련 주의**
> `langchain-neo4j`가 이 클래스를 공식 제공하는지 **이 문서 작성 시점에 확인하지 못했다.**
> 존재 여부를 검증하기 전에는 설계에 포함하지 않는다 — 확인되지 않은 API를 전제로 코드를
> 짜면 구현 도중에 설계를 되돌려야 한다. 쓰고 싶다면 먼저
> ① 설치된 `langchain-neo4j` 버전에서 import가 되는지, ② 현재 `langgraph==1.2.6`의
> `BaseCheckpointSaver` 인터페이스와 맞는지를 확인하고, 그 결과를 이 절에 반영한 뒤
> 진행한다.

---

## 6. LLM 어댑터 공백 — 먼저 메워야 한다

**이 전략의 가장 큰 구현 리스크다.**

`LLMGraphTransformer`(§2), `GraphCypherQAChain`(§3) 같은 LangChain 헬퍼는 인자로 LangChain
`BaseChatModel`을 요구한다. 그런데 [003-langchain_harness.md](003-langchain_harness.md) §4는
배포 서버(EC2)의 디스크·메모리 제약 때문에 **Ollama 대신 `keymaker`를 쓰라**고 정했고,
`keymaker`는 raw google-genai 래퍼라 **`BaseChatModel`이 아니다.** 그대로는 두 헬퍼를 쓸 수 없다.

### 선택지

| 방안 | 평가 |
|---|---|
| **`KeymakerChatModel(BaseChatModel)` 얇은 어댑터를 직접 작성** | **권장.** 새 LLM 벤더 의존성 없이 기존 `GEMINI_API_KEY`를 그대로 재사용하고, 003 §4의 결정을 깨지 않는다. 구현 범위도 `_generate`/`_llm_type` 정도로 작다. |
| `langchain-google-genai` 추가 | 의존성이 늘고 API 키 관리 경로가 `keymaker`와 이원화된다. `keymaker`의 에러 매핑(`MissingApiKeyError`, `format_gemini_error`)도 우회하게 된다. |
| 헬퍼를 안 쓰고 `keymaker`로 프롬프트 직접 작성 | 의존성은 가장 적지만 Text2Cypher·엔티티 추출 프롬프트를 전부 직접 관리해야 한다. 헬퍼가 주는 스키마 강제·파싱을 잃는다. |

`KeymakerChatModel`은 `adapter/outbound/client/`에 두고, 에러 매핑은 기존
`MissingApiKeyError`(503)·`format_gemini_error`를 그대로 재사용한다(003 §4).

---

## 7. 레이어 구성

```
domain/entities/document_graph_entity.py            # 노드·관계의 순수 표현 (neo4j/langchain import 금지)
app/dtos/document_graph_dto.py
app/ports/input/document_graph_use_case.py
app/ports/output/document_graph_index_port.py        # 청크·엔티티 적재 + 벡터 인덱싱
app/ports/output/document_vector_search_port.py      # 벡터 유사도 검색
app/ports/output/document_cypher_port.py             # Text2Cypher 생성·실행 (읽기 전용)
app/ports/output/document_answer_port.py             # 최종 답변 생성
app/use_cases/document_graph_orchestrator.py         # LangGraph StateGraph (§4)
adapter/outbound/repositories/neo4j_document_graph_repository.py  # neo4j 드라이버 세션은 여기서만
adapter/outbound/client/keymaker_chat_model.py       # BaseChatModel 어댑터 (§6)
adapter/outbound/client/document_entity_extractor_client.py       # LangChain + KeymakerChatModel
adapter/outbound/client/document_cypher_client.py                 # LangChain + KeymakerChatModel
adapter/outbound/client/document_answer_client.py                 # LangChain + KeymakerChatModel
adapter/outbound/graph_migrations/                   # 제약·벡터 인덱스 Cypher (002 §5)
adapter/inbound/schema/document_graph_schema.py
adapter/inbound/api/v1/document_graph_router.py
dependencies/document_graph_provider.py
```

기존 5단 구성(포트 → 인터랙터 → 어댑터 → provider → 라우터)을 따른다
([003](003-langchain_harness.md) §0의 `pdf_loader` 패턴).

- `neo4j` 드라이버 세션은 `neo4j_document_graph_repository.py`에서만 연다(002 §3).
- `langchain*` import는 `adapter/outbound/client/`의 파일들에만 존재한다(003 §2·§3).
- `app/use_cases/document_graph_orchestrator.py`의 `StateGraph` 정의는 004 §3이 허용한
  **오케스트레이션 계층 예외**다 — 단, 체인 조립은 여전히 어댑터 책임이다.
- **`domain/document_vector.py`(0바이트 빈 스텁)는 이 작업에서 제거하거나 실제 내용으로
  채운다.** 빈 파일을 방치하지 않는다.

---

## 8. 신규 의존성·환경 변수

### 의존성 — 추가 전 검증할 것

`minho/requirements.txt`에 **아직 없다.** 추가 전에 설치된 `langchain==1.3.11`(v1 계열)과의
호환을 실제로 확인한다 — v1에서 패키지가 재편돼 예전 예제가 그대로 동작하지 않을 수 있다.

| 패키지 | 용도 | 검증 항목 |
|---|---|---|
| `langchain-neo4j` | `Neo4jGraph`, `Neo4jVector`, `GraphCypherQAChain` | `langchain` 1.3.x 호환 |
| `langchain-experimental` | `LLMGraphTransformer` | `langchain` 1.3.x 호환. 안 맞으면 §6 3번안(직접 프롬프트)으로 대체 |
| `langgraph-checkpoint-postgres` | §5 조건 충족 시에만 | `langgraph` 1.2.6의 `BaseCheckpointSaver` 호환 |

`neo4j` 공식 드라이버는 `neo4j-graphrag==1.18.0`이 전이적으로 끌어오지만, **직접 import하는
패키지이므로 `neo4j>=5.0,<6.0`으로 명시적으로 고정한다** — 근거와 절차는
[008-neo4j-strategy.md](008-neo4j-strategy.md) §2.4.

### 환경 변수

[002-neo4j-harness.md](002-neo4j-harness.md) §4가 정한 세 키를 그대로 쓴다. 새 키는 없다 —
LLM은 기존 `GEMINI_API_KEY`(`keymaker`)를 재사용한다(003 §4).

```
NEO4J_URI=bolt://neo4j:7687        # 로컬: bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<루트 .env의 NEO4J_PASSWORD와 동일>
```

- `minho/.env.example`에 추가하고, `docker-compose.yaml`의 `backend.environment`에
  `NEO4J_URI`를 추가한다(002 §4 — **아직 안 돼 있다**).
- `NEO4J_URI` 미설정 시 `document_graph` 라우터만 비활성화하고 나머지 API는 정상 기동해야
  한다(002 §4의 `None` 가드).
- §3의 읽기 전용 사용자를 도입한다면 `NEO4J_READONLY_USER`/`NEO4J_READONLY_PASSWORD`를
  같은 방식으로 추가한다.

---

## 9. 완료 기준 체크리스트

**선행 조건**
- [ ] §0의 표에서 "Neo4j 필요" 쪽 조건이 실제 요구로 확인됐다(아니면 착수하지 않는다).
- [ ] [008-neo4j-strategy.md](008-neo4j-strategy.md) §5의 연결 체크리스트를 먼저 통과했다 — 컨테이너 healthcheck, `NEO4J_URI` 주입, 드라이버 관리자. **연결 없이는 이 문서의 어떤 단계도 시작할 수 없다.**
- [ ] 신규 의존성 3종의 `langchain` 1.3.x / `langgraph` 1.2.6 호환을 실제로 확인한 뒤 `requirements.txt`에 추가했다.

**1단계 — 적재**
- [ ] 벡터 인덱스가 `EMBEDDING_DIM`(768) + `cosine`으로 생성되며, 차원 값을 `vault_keymaker_secret_manager`에서 import한다(중복 정의 없음).
- [ ] 인덱스·제약 Cypher가 `graph_migrations/`에 idempotent(`IF NOT EXISTS`) 스크립트로 있다.
- [ ] 추출 라벨·관계 타입이 화이트리스트로 고정돼 있고 002 §2 표기 규칙을 따른다.
- [ ] 청크 노드와 추출 엔티티가 관계로 연결돼 출처 추적이 가능하다.

**2단계 — 검색**
- [ ] Text2Cypher가 `execute_read`로만 실행된다.
- [ ] 쓰기·스키마 변경 키워드 거부 검사가 있고, 실패 시 벡터 결과만으로 답한다(요청 전체 실패 아님).
- [ ] 생성 쿼리에 `LIMIT`과 드라이버 타임아웃이 강제된다.
- [ ] `allow_dangerous_requests`를 켰다면 위 세 항목이 모두 구현된 뒤다.

**3단계 — LangGraph**
- [ ] Cypher 재생성 루프에 재시도 상한이 있고, 초과 시 벡터 경로로 폴백한다.
- [ ] `domain/`이 `langgraph`·`langchain`·`neo4j`를 import하지 않는다.
- [ ] 노드가 체인을 직접 조립하지 않고 어댑터(포트 구현체)를 호출한다.
- [ ] `graph.compile()`이 요청마다 반복되지 않는다.

**4단계 — 영속성**
- [ ] §5의 도입 조건을 충족했을 때만 Checkpointer를 추가했다.
- [ ] 추가했다면 Postgres 체크포인터를 썼거나, `Neo4jSaver` 실재를 검증한 뒤 이 문서 §5를 갱신했다.

**공통**
- [ ] `KeymakerChatModel` 어댑터가 `adapter/outbound/client/`에 있고, 에러 매핑을 기존 `MissingApiKeyError`/`format_gemini_error`로 재사용한다.
- [ ] `neo4j` 드라이버 세션을 `neo4j_document_graph_repository.py`에서만 연다.
- [ ] `langchain*` import가 `adapter/outbound/client/`에만 있다.
- [ ] `NEO4J_URI` 미설정 시 나머지 API가 죽지 않는다.
- [ ] `domain/document_vector.py` 빈 스텁을 제거했거나 실제 내용으로 채웠다.
- [x] [004-langgraph_harness.md](004-langgraph_harness.md)를 갱신했다 — §1의 Checkpointer 금지 조항을 조건부 허용(§5 참조)으로, §0의 `langgraph_interactor.py` 스텁 서술을 현재 사실(존재하지 않음)로. **이 문서와 함께 완료됨.**
