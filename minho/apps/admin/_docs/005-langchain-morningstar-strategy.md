---
type: spoke
app: silicon_valley
links:
  - star_craft
---

# LangChain 전략 — Morningstar: 맞춤형 금융 인사이트

LangChain은 고객의 요구에 맞춘 맞춤형 솔루션을 제공할 수 있어, 고객 경험을 크게
개선할 수 있습니다. 금융 서비스 제공업체 Morningstar는 LangChain을 사용해 방대한
재무 보고서와 시장 데이터를 분석하고, 이를 바탕으로 사용자 맞춤형 금융 인사이트를
제공하는 인텔리전스 엔진을 개발했습니다. 이 시스템은 금융 전문가들이 복잡한 질문에
대해 정확한 답변을 얻을 수 있도록 도와주며, LangChain의 실시간 데이터 통합과
맞춤형 프롬프팅 기능을 효과적으로 활용하고 있습니다.

## 구현 매핑

이 전략을 아래 `morningstar_insight` 유스케이스로 구현했다.

| 전략 요소 | 구현 |
|-----------|------|
| 방대한 재무 보고서 분석 | [002-neo4j-harness.md](002-neo4j-harness.md)의 PDF 업로드 파이프라인(`graph_pdf_loader`)으로 적재된 보고서를 `document_vector` 테이블에서 재사용 |
| 실시간 데이터 통합 | `MorningstarReportRepository`가 요청 시점마다 최신 보고서를 DB에서 조회 |
| 맞춤형 프롬프팅 | `MorningstarInsightGeneratorClient`의 LangChain `ChatPromptTemplate`이 최신 보고서 컨텍스트 + 사용자 질문을 결합 |
| 인텔리전스 엔진 | `MorningstarInsightInteractor` — 보고서 조회 → LangChain 체인(`prompt \| llm \| parser`) 호출 → 인사이트 반환 |

### 레이어 구성

```
domain/document_vector.py                                      # 기존 재무 보고서 엔티티 재사용
app/dtos/morningstar_insight_dto.py
app/ports/input/morningstar_insight_use_case.py
app/ports/output/morningstar_report_repository_port.py
app/ports/output/morningstar_insight_generator_port.py
app/use_cases/morningstar_insight_interactor.py
adapter/outbound/repository/morningstar_report_repository.py    # 최신 보고서 조회 (실시간)
adapter/outbound/client/morningstar_insight_generator_client.py # LangChain + ChatOllama
adapter/inbound/api/schemas/morningstar_insight_schema.py
adapter/inbound/api/v1/morningstar_insight_router.py            # POST /silicon-valley/morningstar/insight
dependencies/morningstar_insight_provider.py
```

### 환경 변수

로컬 Ollama 서버를 사용한다. 환경변수명은 `docker-compose.yaml`(`OLLAMA_HOST`)·`minho/test.py`(`OLLAMA_MODEL`)의 기존 관례를 따른다 — 상세는 [003-langchain_harness.md](003-langchain_harness.md) §4 참고.

```
OLLAMA_HOST=http://localhost:11434   # Docker: http://host.docker.internal:11434
OLLAMA_MODEL=qwen2.5:3b               # 선택, 미설정 시 어댑터 기본값 사용
```