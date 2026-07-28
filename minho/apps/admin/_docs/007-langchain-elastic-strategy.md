---
type: spoke
app: silicon_valley
links:
  - star_craft
---

# LangChain 전략 — Elastic: 운용 효율성 향상

LangChain은 다양한 데이터 소스와의 통합을 통해 실시간으로 데이터를 처리하고 분석할 수
있어, 비즈니스 운영의 효율성을 크게 향상합니다. Elastic은 보안 분석가들을 지원하기
위해 LangChain을 활용해 AI 어시스턴트를 개발했습니다. 이 AI 어시스턴트는 보안 경고를
요약하고, 워크플로우를 제안하며, 쿼리 생성과 변환을 수행하여 보안 팀의 업무 효율성을
크게 향상합니다. 이 애플리케이션은 실시간으로 대량의 데이터를 처리하고 분석하여 보안
작업을 지원하는데, LangChain의 데이터 통합 및 처리 기능이 중요한 역할을 하고 있습니다.

이 문서의 레이어 배치·환경변수 규칙은 [003-langchain_harness.md](003-langchain_harness.md)를
그대로 따른다 — 이 문서는 그 규칙을 보안 경고 어시스턴트 유스케이스에 매핑한 것이다.

## 0. 전제 조건 — 아직 준비되지 않은 인프라

[002-neo4j-harness.md](002-neo4j-harness.md)의 Neo4j나 006(NCL)의 Postgres 리포지토리와
달리, Elasticsearch는 이 저장소에 **아직 아무것도 없다** — `requirements.txt`에 클라이언트
패키지가 없고, `docker-compose.yaml`에 서비스도 없다. 구현에 들어가기 전에 아래를 먼저
추가한다(이 문서만으로 "이미 연결되어 있다"고 가정하지 않는다).

- `minho/requirements.txt`에 `elasticsearch`(공식 파이썬 클라이언트) 추가. LangChain 쪽에서
  검색 체인을 쓰려면 `langchain-elasticsearch`도 함께 검토한다.
- `docker-compose.yaml`에 `elasticsearch` 서비스 추가(포트·인증은 002의 `neo4j` 서비스 정의
  방식을 그대로 참고 — 비밀번호는 루트 `.env`, 컨테이너 간 URL은 `backend.environment`).
- 이미 운영 중인 Elastic 클러스터(자체 호스팅이 아닌 외부 SaaS)에 붙는 경우, 로컬 컨테이너
  대신 `ELASTICSEARCH_URL`/`ELASTICSEARCH_API_KEY`를 환경변수로만 받고 인프라 자체는
  추가하지 않는다 — 어느 쪽인지 먼저 확인하고 진행한다.

---

## 1. 구현 매핑

이 전략을 아래 `security_insight` 유스케이스로 구현한다.

| 전략 요소 | 구현 |
|-----------|------|
| 다양한 데이터 소스 통합 + 실시간 대량 데이터 처리 | `SecurityAlertIndexPort`가 Elasticsearch에서 최신 보안 경고를 그때그때 조회(재인덱싱·배치 없음) |
| 보안 경고 요약 | `SecurityAlertSummarizerPort` — 조회된 경고 묶음을 LangChain 체인으로 요약 |
| 워크플로우 제안 | `SecurityWorkflowSuggesterPort` — 경고 유형에 맞는 대응 절차를 LangChain 체인으로 제안 |
| 쿼리 생성과 변환 | `SecurityQueryGeneratorPort` — 분석가의 자연어 요청을 Elasticsearch Query DSL/KQL로 생성·변환 |
| 인텔리전스 엔진 | `SecurityInsightOrchestrator` — 분석가 요청의 의도(요약/워크플로우/쿼리)를 분류해 알맞은 포트로 라우팅 |

---

## 2. LangGraph를 쓰는 이유

[006-langchain-ncl-strategy.md](006-langchain-ncl-strategy.md)의 NCL 추천은 조회 → 생성으로
끝나는 단일 순차 흐름이라 LangGraph 없이 003의 LCEL 체인만으로 충분했다. 이번 경우는
[004-langgraph_harness.md](004-langgraph_harness.md) §2의 오른쪽 조건에 해당한다 — 하나의
요청을 "요약", "워크플로우 제안", "쿼리 생성" 중 어디로 보낼지 조건에 따라 나눠야 하고,
생성된 쿼리가 문법적으로 유효하지 않으면 재생성해야 한다. 그래서 `StateGraph`로 구성한다.

```
State: { alert_context, analyst_request, intent, draft_query, query_is_valid, result }

[의도 분류 노드] → (조건부 엣지: intent)
  ├─ "summarize"  → [요약 노드] → END
  ├─ "workflow"   → [워크플로우 제안 노드] → END
  └─ "query"      → [쿼리 생성 노드] → (조건부 엣지: query_is_valid?)
                        ├─ 유효 → END
                        └─ 무효 → [쿼리 생성 노드]로 되돌아감(재시도 상한 필요)
```

- 각 노드는 003의 어댑터(위 포트 구현체)를 호출하는 얇은 wrapper일 뿐, 노드 안에서 새
  LangChain 체인을 즉석으로 조립하지 않는다(004 §3).
- 쿼리 재생성 루프에는 반드시 재시도 횟수 상한을 둔다 — 무한 루프 방지.

---

## 3. 레이어 구성

```
domain/entities/security_alert_entity.py
app/dtos/security_insight_dto.py
app/ports/input/security_insight_use_case.py
app/ports/output/security_alert_index_port.py         # Elasticsearch 조회 (실시간)
app/ports/output/security_alert_summarizer_port.py     # 요약
app/ports/output/security_workflow_suggester_port.py   # 워크플로우 제안
app/ports/output/security_query_generator_port.py      # NL → Query DSL/KQL 생성·변환
app/use_cases/security_insight_orchestrator.py         # LangGraph StateGraph (의도 분기)
adapter/outbound/repositories/elasticsearch_alert_repository.py    # Elasticsearch 클라이언트
adapter/outbound/client/security_alert_summarizer_client.py        # LangChain + ChatOllama
adapter/outbound/client/security_workflow_suggester_client.py      # LangChain + ChatOllama
adapter/outbound/client/security_query_generator_client.py         # LangChain + ChatOllama
adapter/inbound/api/schemas/security_insight_schema.py
adapter/inbound/api/v1/security_insight_router.py                 # POST /silicon-valley/security/insight
dependencies/security_insight_provider.py
```

- `elasticsearch_alert_repository.py`에서만 Elasticsearch 클라이언트를 연다(002 §3의 "드라이버
  세션은 어댑터 계층에만" 규칙과 동일 원칙).
- 세 LangChain 클라이언트(`*_client.py`)에서만 LangChain을 import한다(003 §2·§3). `domain/`,
  `app/ports/`, `app/use_cases/`(오케스트레이터의 `StateGraph` 정의 자체는 예외로 허용되지만,
  체인 조립은 여전히 어댑터 책임 — 004 §3)는 `langchain*`을 import하지 않는다.

---

## 4. 환경 변수

```
ELASTICSEARCH_URL=http://localhost:9200   # 또는 운영 중인 Elastic 클러스터 엔드포인트
ELASTICSEARCH_API_KEY=                     # 선택 — SaaS/보안 클러스터 인증 시
```

로컬 Ollama 서버는 [003-langchain_harness.md](003-langchain_harness.md) §4의 관례를 그대로
따른다.

```
OLLAMA_HOST=http://localhost:11434   # Docker: http://host.docker.internal:11434
OLLAMA_MODEL=qwen2.5:3b               # 선택, 미설정 시 어댑터 기본값 사용
```

- `minho/.env.example`에 위 네 키를 주석과 함께 추가한다.
- `ELASTICSEARCH_URL` 미설정 시에도 나머지 API가 죽지 않도록, 리포지토리 생성자에서
  접속 실패를 라우터 레벨의 503으로 변환한다(`database.py`가 `DATABASE_URL` 미설정을
  다루는 패턴과 동일 — 002 §4 참고).

---

## 5. 완료 기준 체크리스트

- [ ] `elasticsearch`(및 필요 시 `langchain-elasticsearch`)를 `minho/requirements.txt`에 추가했다.
- [ ] `docker-compose.yaml`에 `elasticsearch` 서비스(또는 외부 클러스터 연결 확인)를 추가했다.
- [ ] `domain/`, `app/ports/`, `app/use_cases/`에 `langchain*` import 없음.
- [ ] `elasticsearch_alert_repository.py`에서만 Elasticsearch 클라이언트를 연다.
- [ ] 세 `*_client.py`에서만 LangChain 체인을 조립한다.
- [ ] 쿼리 재생성 루프에 재시도 횟수 상한이 있다.
- [ ] `ELASTICSEARCH_URL`/`ELASTICSEARCH_API_KEY`/`OLLAMA_HOST`/`OLLAMA_MODEL`이 `minho/.env.example`에 추가돼 있다.
- [ ] `ELASTICSEARCH_URL` 미설정 시 나머지 API가 죽지 않는다.
