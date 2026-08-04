# LANGGRAPH-HARNESS.md

`apps/admin`에서 LangGraph(상태 그래프 기반 오케스트레이션)를 다룰 때 지키는 규칙. 라이브러리(`minho/requirements.txt`의 `langgraph==1.2.6`)는 이미 설치되어 있지만 저장소 어떤 코드에서도 아직 import되지 않았고, `app/use_cases/`에 LangGraph용 파일도 아직 없다. 이 문서는 그 첫 구현 시점에 지킬 규칙이다. 프롬프트·검색·생성 체인 자체의 규칙은 [003-langchain_harness.md](003-langchain_harness.md) 소관이며, 이 문서는 **여러 단계를 잇는 실행 흐름(노드/엣지)** 범위로 한정한다.

---

## 0. 컨텍스트

- "그래프"라는 단어가 [002-neo4j-harness.md](002-neo4j-harness.md)(Neo4j 그래프 DB)와 이 문서(LangGraph 상태 그래프)에서 전혀 다른 뜻으로 쓰인다 — 혼동 주의. LangGraph의 노드·엣지는 DB에 저장되는 데이터가 아니라 **코드로 정의되는 실행 흐름**이고, 영속화가 필요하면 여전히 002/기존 리포지토리 포트를 거친다.
- 이 문서의 초판은 `app/use_cases/langgraph_interactor.py`라는 빈 스텁이 존재한다고 서술했으나, **그 파일은 현재 존재하지 않는다**(`langchain_morningstar_interactor.py`도 마찬가지). 스텁이 있으니 채운다는 식으로 도입 근거를 삼지 않는다 — 도입 여부는 언제나 §2 표로만 판단한다.
- 첫 도입 대상으로 검토 중인 흐름은 [009-langgraph-strategy.md](009-langgraph-strategy.md)의 `document_graph`(GraphRAG 하이브리드 검색)다 — 라우팅과 Cypher 재생성 루프가 있어 §2 오른쪽 조건에 해당한다.

---

## 1. LangGraph 핵심 개념 (이 저장소 관점)

- **State**: 그래프 실행 중 노드 사이를 오가는 상태. `TypedDict` 또는 `dataclass`로 정의하고, `domain/`의 영속 엔티티(`MorningstarInsightEntity` 등)를 그대로 재사용하지 않는다 — 실행 중간 상태와 영속 엔티티는 다른 개념이다.
- **Node**: 상태를 입력받아 일부를 갱신해 반환하는 함수 하나. 노드 안에서 새 LangChain 체인을 즉석으로 만들지 않는다 — 003 어댑터(`FinancialDocumentIndexPort`, `FinancialInsightAnswererPort` 구현체)를 호출하는 얇은 wrapper로만 둔다.
- **Edge / 조건부 엣지**: 노드 간 흐름 제어. 단순 순차 흐름이면 엣지가 아니라 §2 기준에 따라 LangGraph 자체를 도입하지 않는다.
- **Checkpointer**: 대화·작업 상태를 세션 간 이어가기 위한 영속 저장소. **기본은 여전히 도입하지 않는 것(YAGNI)** 이며, 아래 조건이 실제로 확인됐을 때만 예외로 허용한다.
  - **조건**: 흐름이 멀티턴이 되어 이전 턴의 상태를 다음 턴에서 이어 써야 하고, 그 세션이 프로세스 재시작을 넘어 유지되어야 한다. 단일 요청-응답(질문 하나 → 답변 하나)이면 붙이지 않는다.
  - **저장소**: 새 인프라를 추가하지 말고 이미 떠 있는 Postgres를 재사용한다(`langgraph-checkpoint-postgres`). 상세 근거와 검증 절차는 [009-langgraph-strategy.md](009-langgraph-strategy.md) §5.

---

## 2. LangChain 체인(003)이 아니라 LangGraph를 쓰는 기준

| 상황 | 선택 |
|---|---|
| 색인 → 검색 → 생성이 한 번의 순차 흐름으로 끝남 | 003의 LCEL 체인(`prompt \| llm \| parser`)으로 충분 — LangGraph 도입 금지 |
| 검색 결과가 없으면 색인 단계로 되돌아가거나, 답변 신뢰도가 낮으면 재검색해야 함 | 조건부 엣지가 있는 `StateGraph`로 표현 |
| 하나의 요청이 여러 유스케이스(색인 확인, 질의응답, 이력 저장)를 조건에 따라 순서를 바꿔가며 호출해야 함 | `StateGraph`로 오케스트레이션 |

`StateGraph`를 쓰는 파일을 만들기 전에 이 표로 필요성부터 확인한다 — 위 왼쪽 열(단순 순차 흐름)에 해당하면 파일을 만들지 말고 003의 LCEL 인터랙터로 처리한다. 빈 스텁이나 파일 이름이 이미 있다는 이유만으로 LangGraph를 구현하지 않는다.

---

## 3. 이 저장소의 구성 규칙

- `StateGraph` 정의는 `app/use_cases/`에 둔다 — 실행 흐름 자체는 유스케이스의 책임이므로, 002/003의 "LangChain/드라이버 import는 adapter에만" 규칙의 예외로 취급한다. 단, 각 노드가 호출하는 개별 LangChain 체인 조립은 여전히 `adapter/outbound/`에 있어야 한다(003 규칙 그대로 유지 — 예외는 오케스트레이션 계층에만 적용).
- 노드 함수는 외부 I/O(DB 조회, LLM 호출)를 직접 하지 않고 반드시 포트(`app/ports/output/`)를 통해서만 수행한다 — 002/003과 동일한 포트 재사용 원칙.
- `graph.compile()`은 요청마다 새로 하지 않는다 — 모듈 로드 시 한 번 컴파일해 재사용한다(`StateGraph` 정의 자체는 무상태라 안전).
- 노드 이름·상태 키는 영어 snake_case로 통일한다(002 §2의 명명 원칙과 동일).

---

## 4. 완료 기준 체크리스트

- [ ] `StateGraph` 파일을 만들기 전에 §2 표로 LangGraph가 실제로 필요한지 확인했다(필요 없으면 003의 LCEL 인터랙터로 처리한다).
- [ ] `domain/`이 `langgraph`를 import하지 않는다 — State는 별도 `TypedDict`/`dataclass`로 정의돼 있다.
- [ ] 노드 함수가 LangChain 체인을 직접 조립하지 않고 003의 어댑터(포트 구현체)를 호출한다.
- [ ] 노드의 외부 I/O가 전부 포트를 통해서만 일어난다.
- [ ] `graph.compile()`이 요청마다 반복 호출되지 않는다.
- [ ] Checkpointer 등 상태 영속 기능은 §1의 조건이 확인되기 전에는 추가하지 않았다. 추가했다면 Postgres 체크포인터를 썼다([009](009-langgraph-strategy.md) §5).
