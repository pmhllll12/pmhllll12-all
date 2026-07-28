# LANGCHAIN-HARNESS.md

`apps/admin`에서 LangChain으로 LLM 체인(프롬프트·검색·생성)을 다룰 때 지키는 규칙. 라이브러리(`minho/requirements.txt`의 `langchain==1.3.11`, `langchain-ollama==1.1.0`, `langchain-text-splitters==1.1.2`, `langsmith==0.9.3`)는 이미 설치되어 있고, 이 문서는 **그 위에서 체인을 어떻게 설계·배치할지**를 정한다. LangGraph(그래프형 오케스트레이션)는 별도 [004-langgraph_harness.md](004-langgraph_harness.md) 소관이며, 이 문서는 LCEL 체인·프롬프트·리트리버 범위로 한정한다.

---

## 0. 컨텍스트

- 진행 중인 도입 지점: 재무 보고서 RAG 질의응답 유스케이스의 포트·DTO·엔티티가 먼저 정의돼 있다 — `app/ports/output/financial_document_index_port.py`(색인), `app/ports/output/financial_insight_answerer_port.py`(질의응답), `app/ports/output/morningstar_insight_port.py`(이력 저장), `app/dtos/morningstar_insight_dto.py`, `domain/entities/morningstar_insight_entity.py`. 실제 LangChain 호출부(`app/use_cases/langchain_morningstar_interactor.py`)와 어댑터는 아직 빈 스텁 — 이 문서는 그 구현 시점에 지킬 규칙이다.
- [005-langchain-morningstar-strategy.md](005-langchain-morningstar-strategy.md)가 처음 그렸던 레이어 매핑(`MorningstarInsightGeneratorClient`, `MorningstarReportRepository` 등)과 위 실제 포트 이름이 갈라졌다 — 어느 쪽이 최종본이든, 이 문서의 규칙(§2~§4)은 이름과 무관하게 적용된다. 구현을 마치면 005 문서의 레이어 매핑 표를 실제 파일명으로 갱신한다.
- 참고 구현 패턴: `pdf_loader` 스포크(`app/ports/input/pdf_loader_use_case.py` → `app/use_cases/pdf_loader_interactor.py` → `adapter/outbound/repositories/pdf_loader_repository.py` → `dependencies/pdf_loader_provider.py` → `adapter/inbound/api/v1/pdf_loader_router.py`)가 이미 완성돼 있다. 새 LangChain 유스케이스도 동일한 5단 구성(포트 → 인터랙터 → 어댑터 → provider → 라우터)을 따른다.
- 텍스트 추출은 기존 `adapter/outbound/neo4j_graphrag_pdf_text_extractor.py`([002-neo4j-harness.md](002-neo4j-harness.md))를 재사용한다 — LangChain은 그 다음 단계(분할 → 색인 → 검색 → 생성)만 담당하고, PDF 파싱 파이프라인을 중복 구현하지 않는다.

---

## 1. LangChain으로 담당하는 4단계 (실제 유스케이스 매핑)

| 일반적 LangChain 기능 | 이 저장소의 구현 지점 |
|---|---|
| 다양한 데이터 소스 통합 | `FinancialDocumentIndexPort.index` — 추출된 텍스트를 청크로 분할해 벡터 인덱스에 저장 |
| 유연한 프롬프팅·컨텍스트 관리 | `FinancialInsightAnswererPort.answer` — 질문과 관련된 청크를 검색(retriever)한 뒤 `ChatPromptTemplate`으로 컨텍스트+질문을 결합 |
| 파인튜닝·커스터마이징 | LLM 교체 가능성은 포트 뒤에 숨긴다 — 현재 Ollama, 추후 다른 모델로 바꿔도 `FinancialInsightAnswererPort` 시그니처는 그대로 |
| 데이터 반응형 애플리케이션 | 재인덱싱 없이 매 요청 시점의 최신 색인 상태를 그대로 검색·반영 |

---

## 2. 이 저장소의 구성 규칙

- LangChain import는 `adapter/outbound/`에만 존재한다 — `domain/`, `app/ports/`는 순수 인터페이스·dataclass만 두고 `langchain*` import를 하지 않는다([002-neo4j-harness.md](002-neo4j-harness.md) §3과 동일 원칙).
- 체인은 LCEL(`prompt | llm | StrOutputParser()`)로 구성하고, 어댑터 클래스의 메서드 안에서 조립한다. 체인 객체를 모듈 전역 싱글턴으로 두지 않는다 — 요청마다 필요한 컨텍스트(검색된 청크 등)를 그때그때 주입한다.
- 텍스트 분할은 `langchain-text-splitters`의 `RecursiveCharacterTextSplitter`를 쓰고, `chunk_size`/`chunk_overlap`은 어댑터 상수로 명시한다(매직 넘버 금지).
- LLM은 `langchain-ollama`의 `ChatOllama`를 기본으로 하되, 모델명·서버 주소는 반드시 환경변수로 받는다(§4) — 코드에 하드코딩하지 않는다.
- 벡터 저장소를 새로 고르기 전에 기존 자원(Neon Postgres의 pgvector 확장 등) 재사용 가능 여부를 먼저 확인한다. 정말 필요할 때만 `docker-compose.yaml`에 새 인프라를 추가한다 — 요청 범위를 넘는 과설계는 만들지 않는다(루트 [CLAUDE.md](../../../../CLAUDE.md) 4원칙).

---

## 3. 헥사고날 계층에서의 위치

`minho/_docs/architecture-star-topology.md`가 정한 `domain → app → adapter` 경계를 LangChain 체인에도 그대로 적용한다.

- `domain/`: `MorningstarInsightEntity` 같은 순수 파이썬 엔티티만 둔다. LangChain 타입(`Document`, `BaseMessage` 등)을 그대로 노출하지 않는다.
- `app/ports/output/`: `FinancialDocumentIndexPort`, `FinancialInsightAnswererPort`처럼 추상 인터페이스만 정의한다. 유스케이스(인터랙터)는 이 포트만 의존한다.
- `app/use_cases/`: `langchain_morningstar_interactor.py` — 포트를 호출해 색인·질의응답 흐름을 조합한다. LangChain을 직접 import하지 않는다(그건 어댑터 책임).
- `adapter/outbound/`: 포트 구현체가 실제로 `ChatPromptTemplate`, `RecursiveCharacterTextSplitter`, `ChatOllama`를 조립한다. LangChain 의존성은 이 계층에만 존재해야 한다.
- `dependencies/`: `pdf_loader_provider.py`처럼 FastAPI `Depends` 체인으로 포트 구현체를 조립해 인터랙터에 주입한다.

---

## 4. 연결 설정

로컬 Ollama 서버를 사용한다. 이 저장소의 실제 관례는 `OLLAMA_HOST`(서버 주소)·`OLLAMA_MODEL`(모델명)이다 — `docker-compose.yaml`의 `backend.environment`가 `OLLAMA_HOST`를 주입하고, `minho/test.py`가 `os.getenv("OLLAMA_MODEL")`을 기본값과 함께 읽는 패턴을 그대로 따른다. `core/lol/t1_mid_faker_orchestrator.py`는 모델명을 코드에 하드코딩하고 환경변수를 전혀 읽지 않는 예외 사례이므로 참고하지 않는다 — 새 LangChain 어댑터는 두 값 모두 반드시 환경변수로 읽는다.

```
OLLAMA_HOST=http://localhost:11434   # Docker: http://host.docker.internal:11434 (docker-compose.yaml 참고)
OLLAMA_MODEL=qwen2.5:3b               # 선택, 미설정 시 어댑터 기본값 사용
```

- `minho/.env.example`에 위 두 키를 주석과 함께 추가한다.
- `langchain-ollama`의 `ChatOllama(base_url=..., model=...)`에 위 두 환경변수 값을 그대로 전달한다 — `base_url` 인자명과 환경변수명(`OLLAMA_HOST`)이 다르다고 임의로 `OLLAMA_BASE_URL` 같은 새 이름을 만들지 않는다.
- `OLLAMA_HOST` 미설정 시에도 나머지 API가 죽지 않도록, 어댑터 생성자에서 접속 실패를 라우터 레벨의 503 등으로 변환한다(`database.py`가 `DATABASE_URL` 미설정을 다루는 패턴과 동일).

---

## 5. 장단점 — 도입 판단 기준

- **성능**: 체인 단계(검색 → 프롬프트 조립 → 생성)가 늘어날수록 지연이 커진다. 실시간 응답이 필요한 엔드포인트는 단계를 추가하기 전에 실제로 필요한지 먼저 검증한다.
- **러닝 커브**: LCEL 최소 형태(`prompt | llm | parser`)로 시작하고, 메모리·에이전트·복잡한 리트리버 체인 같은 고급 기능은 요구사항이 생겼을 때만 추가한다.
- **부적합 사례**: 단일 프롬프트 1회 호출이면 충분한 경우(`core/lol/t1_mid_faker_orchestrator.py`처럼 raw `ollama` 클라이언트로 이미 해결된 사례)에는 LangChain을 억지로 끼워넣지 않는다 — 프롬프트 템플릿·리트리버 조합이 실제로 필요한 곳(재무 문서 RAG처럼 컨텍스트 검색이 필요한 경우)에만 도입한다.

---

## 6. 완료 기준 체크리스트

- [ ] `domain/`, `app/ports/`, `app/use_cases/`에 `langchain*` import 없음.
- [ ] `adapter/outbound/`에서만 LangChain 체인(prompt·splitter·LLM)을 조립한다.
- [ ] LLM 모델명·서버 주소가 환경변수로 주입되고 코드에 하드코딩되지 않는다.
- [ ] 텍스트 분할의 `chunk_size`/`chunk_overlap`이 상수로 명시돼 있다.
- [ ] 새 벡터 저장소 인프라를 추가하기 전 기존 자원(pgvector 등) 재사용 여부를 검토했다.
- [ ] `minho/.env.example`에 `OLLAMA_BASE_URL`/`OLLAMA_MODEL` 추가.
- [ ] `OLLAMA_BASE_URL` 미설정 시 나머지 API가 죽지 않는다.
- [ ] 구현 완료 후 [005-langchain-morningstar-strategy.md](005-langchain-morningstar-strategy.md)의 레이어 매핑 표를 실제 파일명으로 갱신했다.
