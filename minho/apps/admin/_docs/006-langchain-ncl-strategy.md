---
type: spoke
app: silicon_valley
links:
  - star_craft
---

# LangChain 전략 — NCL: 최적화된 여행 계획 제공

LangChain은 사용자 맞춤형 프롬프팅 및 파인튜닝 기능을 통해 특정 산업의 요구에 맞춘
솔루션을 제공합니다. NCL(노르웨이 크루즈 라인)은 LangChain을 이용해 고객들이 이상적인
크루즈 여행을 계획할 수 있도록 돕는 AI 어시스턴트를 개발했습니다. 이 시스템은 고객의
선호도와 탐색 기록을 기반으로 맞춤형 추천을 제공하며, LangChain을 통해 실시간으로
변화하는 고객 요구에 대응할 수 있습니다.

이 문서의 레이어 배치·환경변수 규칙은 [003-langchain_harness.md](003-langchain_harness.md)를
그대로 따른다 — 이 문서는 그 규칙을 NCL 여행 추천 유스케이스에 매핑한 것이다.

## 구현 매핑

이 전략을 아래 `ncl_trip_planner` 유스케이스로 구현한다.

| 전략 요소 | 구현 |
|-----------|------|
| 고객 선호도 기반 맞춤 추천 | `NclCustomerPreferencePort`가 저장된 선호도(선호 목적지·선실 등급·예산 등)를 조회 |
| 탐색 기록 반영 | `NclBrowsingHistoryPort`가 최근 탐색 로그(조회한 항로·상품)를 조회 |
| 실시간 데이터 통합 | `NclTripPlannerInteractor`가 매 요청마다 최신 선호도·탐색 기록을 DB에서 조회해 반영 — 별도 재학습·배치 없이 요청 시점 값을 그대로 사용 |
| 맞춤형 프롬프팅 | `NclTripRecommenderClient`의 `ChatPromptTemplate`이 선호도 + 탐색 기록 + 고객 질문을 컨텍스트로 결합 |
| 인텔리전스 엔진 | `NclTripPlannerInteractor` — 선호도·탐색 기록 조회 → LangChain 체인(`prompt \| llm \| parser`) 호출 → 추천 결과 반환 |

### LangGraph를 쓰지 않는 이유

선호도 조회 → 탐색 기록 조회 → 추천 생성은 조건 분기·재시도가 없는 단일 순차 흐름이다.
[004-langgraph_harness.md](004-langgraph_harness.md) §2 기준에 따라 이 유스케이스는
LangGraph `StateGraph`가 아니라 003의 LCEL 체인만으로 구현한다 — 나중에 "추천 신뢰도가
낮으면 선호도를 다시 물어본다" 같은 분기가 실제로 필요해지면 그때 LangGraph 전환을
검토한다.

### 레이어 구성

```
domain/entities/ncl_trip_recommendation_entity.py
app/dtos/ncl_trip_planner_dto.py
app/ports/input/ncl_trip_planner_use_case.py
app/ports/output/ncl_customer_preference_port.py
app/ports/output/ncl_browsing_history_port.py
app/ports/output/ncl_trip_recommender_port.py
app/use_cases/ncl_trip_planner_interactor.py
adapter/outbound/repositories/ncl_customer_preference_repository.py   # 선호도 조회 (Postgres)
adapter/outbound/repositories/ncl_browsing_history_repository.py      # 탐색 기록 조회 (Postgres)
adapter/outbound/client/ncl_trip_recommender_client.py                # LangChain + ChatOllama
adapter/inbound/api/schemas/ncl_trip_planner_schema.py
adapter/inbound/api/v1/ncl_trip_planner_router.py                    # POST /silicon-valley/ncl/trip-plan
dependencies/ncl_trip_planner_provider.py
```

- 선호도·탐색 기록은 문서(PDF)가 아니라 정형 데이터이므로 [002-neo4j-harness.md](002-neo4j-harness.md)의
  그래프 파이프라인이나 벡터 색인은 필요 없다 — `pdf_loader`가 아니라 기존 `piper_*_repository.py`류의
  단순 Postgres 리포지토리 패턴을 재사용한다.
- `NclTripRecommenderClient`만 LangChain을 import한다(003 §2·§3의 "LangChain import는
  `adapter/outbound/`에만" 규칙). `domain/`, `app/ports/`, `app/use_cases/`는 `langchain*`을
  import하지 않는다.

### 환경 변수

로컬 Ollama 서버를 사용한다. 환경변수명은 [003-langchain_harness.md](003-langchain_harness.md) §4의
관례(`OLLAMA_HOST`/`OLLAMA_MODEL`)를 그대로 따른다.

```
OLLAMA_HOST=http://localhost:11434   # Docker: http://host.docker.internal:11434
OLLAMA_MODEL=qwen2.5:3b               # 선택, 미설정 시 어댑터 기본값 사용
```

## 완료 기준 체크리스트

- [ ] `domain/`, `app/ports/`, `app/use_cases/`에 `langchain*` import 없음.
- [ ] `NclTripRecommenderClient`(어댑터)에서만 LangChain 체인을 조립한다.
- [ ] 선호도·탐색 기록 조회가 매 요청마다 최신 상태를 반영한다(캐시로 인한 stale 추천 없음).
- [ ] `OLLAMA_HOST`/`OLLAMA_MODEL`이 `minho/.env.example`에 추가돼 있다.
- [ ] 조건 분기가 실제로 필요해지기 전까지 LangGraph를 도입하지 않았다.
