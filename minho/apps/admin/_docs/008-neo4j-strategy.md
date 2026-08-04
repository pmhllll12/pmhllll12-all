---
type: spoke
app: silicon_valley
links:
  - star_craft
---

# Neo4j 전략 — 컨테이너 기동과 실제 연결

[002-neo4j-harness.md](002-neo4j-harness.md) §4와 [009-langgraph-strategy.md](009-langgraph-strategy.md) §9가
모두 **선행 조건**으로 지목한 격차를 메우는 문서다 — Neo4j 컨테이너는 `docker-compose.yaml`에
정의돼 있지만, **앱 코드가 실제로 접속하는 경로가 아직 없다.**

이 문서는 **컨테이너 기동 → 환경 변수 → 드라이버 연결**까지만 다룬다.

- 노드·라벨·관계·속성의 **모델링 규칙**은 [002-neo4j-harness.md](002-neo4j-harness.md) 소관.
- GraphRAG **추론·검색 전략**은 [009-langgraph-strategy.md](009-langgraph-strategy.md) 소관.
- 이 문서는 그 둘이 딛고 설 **연결 기반**만 정한다.

---

## 0. 현재 상태 (검증 완료)

### 이미 있는 것

| 항목 | 위치 |
|------|------|
| `neo4j` 서비스 — `image: neo4j:5-community`, 포트 `7474`/`7687`, `NEO4J_AUTH`, 볼륨 `neo4j_data` | `docker-compose.yaml` |
| `backend` 서비스의 `depends_on: [pgvector, neo4j, redis]` | `docker-compose.yaml` |
| `NEO4J_PASSWORD` | **루트 `.env`** (compose가 `${NEO4J_PASSWORD}`로 보간) |
| `neo4j-graphrag==1.18.0` | `minho/requirements.txt` |

`neo4j` 서비스에 `networks:`가 지정돼 있지 않아 compose 기본 네트워크에만 속한다. 다른 서비스도
모두 기본 네트워크를 쓰므로 서비스명(`neo4j`)으로 접속 가능하다 — **변경할 이유가 없다.**

`neo4j-graphrag`는 현재 `adapter/outbound/neo4j_graphrag_pdf_text_extractor.py`에서 **PDF 텍스트
추출(`PdfLoader`, 내부적으로 pypdf)에만** 쓰인다. 이 코드는 **Neo4j에 접속하지 않는다** —
패키지 이름 때문에 "이미 그래프 DB를 쓰고 있다"고 오해하기 쉬우니 주의한다.

### 아직 없는 것

- **`NEO4J_URI`, `NEO4J_USER`** — `minho/.env.example`에는 Neo4j 키가 **하나도 없고**,
  `docker-compose.yaml`의 `backend.environment`에도 주입되지 않는다. 즉 컨테이너 안의 앱은
  Neo4j 주소를 모른다. ([002](002-neo4j-harness.md) §4가 지적한 그대로 — 아직 미해결)
- **healthcheck** — `depends_on: neo4j`는 "컨테이너가 시작됐다"만 보장하고 "Bolt가 쿼리를 받을
  준비가 됐다"는 보장하지 않는다. Neo4j는 기동에 수십 초가 걸려 초기 요청이 실패한다.
- **드라이버를 여는 코드** — `minho/core/matrix/`에 Neo4j 연결 관리자가 없다.
- **출력 포트/어댑터** — 009 §7이 설계한 `neo4j_document_graph_repository.py`가 아직 없다.
- **`neo4j` 드라이버의 명시적 버전 핀** — `minho/requirements.txt`에 `neo4j`가 직접 없다(§2.4).

---

## 1. 설계 결정 — 같은 컨테이너, 라벨로 분리

Neo4j를 쓰려는 목적이 두 갈래다.

| 용도 | 문서 | 상태 |
|------|------|------|
| GraphRAG 지식 그래프 (문서 엔티티·관계) | [009-langgraph-strategy.md](009-langgraph-strategy.md) | 설계됨 — 이 문서의 주 대상 |
| 허브 온톨로지 인덱스 (앱 노드·관계) | [`minho/_docs/architecture-star-topology.md`](../../../_docs/architecture-star-topology.md) | **미구현** — `minho/apps/star_craft/` 디렉터리 자체가 아직 없다 |

`neo4j:5-community`는 커뮤니티 에디션이라 **멀티 데이터베이스(`CREATE DATABASE`)를 지원하지
않는다**(엔터프라이즈 전용). 별도 컨테이너를 띄우는 대신 **같은 컨테이너·같은 기본
데이터베이스를 공유하되 라벨을 네임스페이스로 분리**한다.

- GraphRAG: `DocumentChunk`, `Entity` 등 문서 도메인 라벨 (실제 라벨은 009 §2의 화이트리스트로 확정)
- 허브 온톨로지: `Hub`, `Spoke` — **star_craft가 실제로 만들어질 때** 확정한다

Cypher는 항상 라벨로 범위를 좁혀 두 그래프가 섞이지 않게 한다. 컨테이너·자격증명·드라이버
관리자는 하나면 된다.

> 허브 온톨로지 쪽은 **아직 앱이 없으므로 이 문서의 구현 범위가 아니다.** 라벨 분리 원칙만
> 미리 정해 두어, 나중에 star_craft를 만들 때 데이터가 충돌하지 않게 한다.

---

## 2. 구현 전략

### 2.1 healthcheck 추가

`docker-compose.yaml`의 `neo4j` 서비스에 추가한다.

```yaml
  neo4j:
    image: neo4j:5-community
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}
    volumes:
      - neo4j_data:/data
    healthcheck:
      test: ["CMD-SHELL", "cypher-shell -u neo4j -p \"$$NEO4J_PASSWORD\" 'RETURN 1' || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 10
      start_period: 30s
    restart: always
```

- `$$`는 compose 변수 보간을 피해 **컨테이너 내부 셸**에 `$NEO4J_PASSWORD`를 넘기기 위한 이스케이프다.
  단, `neo4j` 컨테이너 환경에는 `NEO4J_AUTH`만 있고 `NEO4J_PASSWORD`는 없다 — healthcheck에서
  쓰려면 `environment`에 `NEO4J_PASSWORD: ${NEO4J_PASSWORD}`를 **함께 추가**해야 한다.
  (추가하기 싫다면 인증이 필요 없는 `wget -qO- http://localhost:7474 || exit 1`로 대체한다.)

`backend`의 `depends_on`을 조건부로 강화한다. **현재는 짧은 리스트 형식이므로 매핑 형식으로
바꿔야 하고, 이때 `pgvector`·`redis`도 함께 옮겨 적어야 한다** — 하나만 매핑으로 바꾸면 나머지가
누락된다.

```yaml
    depends_on:
      pgvector:
        condition: service_started
      redis:
        condition: service_started
      neo4j:
        condition: service_healthy
```

### 2.2 접속 정보 환경 변수

[002-neo4j-harness.md](002-neo4j-harness.md) §4가 정한 세 키를 그대로 쓴다. `minho/.env.example`에
추가한다(현재 Neo4j 키가 전혀 없다).

```text
NEO4J_URI=bolt://neo4j:7687   # compose 네트워크 내부에서는 서비스명으로 접속
NEO4J_USER=neo4j
NEO4J_PASSWORD=               # 루트 .env의 NEO4J_PASSWORD와 같은 값이어야 인증을 통과한다
```

`docker-compose.yaml`의 `backend.environment`에는 `NEO4J_URI: bolt://neo4j:7687`을 추가한다.
`backend`는 이미 `env_file: ./minho/.env`를 읽으므로 `NEO4J_USER`/`NEO4J_PASSWORD`는 그쪽으로 들어간다.

> **비밀번호가 두 파일에 나뉘어 있다.** compose의 `neo4j` 서비스는 **루트 `.env`** 의
> `NEO4J_PASSWORD`로 계정을 만들고, `backend`는 **`minho/.env`** 를 읽는다. 두 값이 다르면
> 컨테이너는 정상 기동하는데 앱만 인증에 실패한다 — 진단하기 어려운 실패이므로 §3에서 먼저 확인한다.

로컬에서 `minho/CLAUDE.md`의 실행법(`uvicorn --reload`, 컨테이너 밖)으로 개발할 때는
`docker compose up -d neo4j`로 컨테이너만 띄우고 `minho/.env`에서
`NEO4J_URI=bolt://localhost:7687`로 덮어쓴다(포트가 이미 호스트에 퍼블리시돼 있다).

### 2.3 연결 관리자 (신규 — 설계 초안, 미구현)

`minho/database.py`가 Postgres에 쓰는 **방어적 패턴**을 그대로 따른다 — 모듈 로드 시 한 번
초기화하되, 환경 변수가 없거나 접속에 실패하면 **예외를 던지지 않고 `None`으로 두어 앱 전체가
죽지 않게** 한다(`engine = None` + `get_db_optional()`).

> `core/matrix/grid_oracle_database_manager.py`는 31줄짜리 **재export 셔임**이고 실제 로직은
> `minho/database.py`에 있다. 패턴을 참고할 때는 `database.py`를 본다.

Matrix 세계관 명명 관례(`grid_oracle_*`, `grid_morpheus_*`, `grid_neo_*`)를 따라
`minho/core/matrix/grid_architect_graph_manager.py`로 둔다 — 그래프 구조 전체를 설계하는
"Architect"에서 따왔다.

```python
from __future__ import annotations

import logging
import os

from neo4j import AsyncDriver, AsyncGraphDatabase

logger = logging.getLogger(__name__)

driver: AsyncDriver | None = None


def _build_driver() -> None:
    """NEO4J_URI가 없으면 조용히 비활성화한다 — 나머지 API는 정상 기동해야 한다."""
    global driver

    uri = os.getenv("NEO4J_URI")
    if not uri:
        logger.info("[graph] NEO4J_URI 미설정 — 그래프 기능을 비활성화합니다.")
        driver = None
        return

    try:
        driver = AsyncGraphDatabase.driver(
            uri,
            auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "")),
        )
    except Exception:
        logger.exception("[graph] Neo4j 드라이버 초기화 실패 — 그래프 기능을 비활성화합니다.")
        driver = None


_build_driver()


def get_driver_optional() -> AsyncDriver | None:
    """드라이버가 없으면 None. 호출부(어댑터)가 503으로 변환한다."""
    return driver


async def dispose_driver() -> None:
    global driver
    if driver is not None:
        await driver.close()
    driver = None
```

- **`get_driver()`가 아니라 `get_driver_optional()`이다.** 미설정 시 예외를 던지면 라우터 등록
  시점에 앱이 죽어 002 §4의 "나머지 API는 정상 기동" 요구를 어긴다.
- `AsyncGraphDatabase.driver()`는 **지연 연결**이라 생성 시점에 접속을 검증하지 않는다.
  실제 도달 가능 여부는 첫 쿼리에서 드러나므로, 어댑터가 그 예외를 503으로 변환해야 한다.
- `main.py`의 `lifespan` 종료 훅에 `dispose_driver()`를 연결한다.

### 2.4 requirements.txt — 드라이버를 명시적으로 고정한다

```text
neo4j>=5.0,<6.0   # neo4j-graphrag의 전이 의존성에 기대지 않고 직접 고정
```

`neo4j-graphrag==1.18.0`이 `neo4j` 드라이버를 전이적으로 끌어오지만, **직접 import하는 패키지는
직접 명시한다.** 그러지 않으면 `neo4j-graphrag`를 올리거나 걷어낼 때 드라이버 버전이 조용히
바뀌거나 사라진다.

> **[009](009-langgraph-strategy.md) §8 정정** — 009는 "`neo4j-graphrag`가 이미 있으므로 `neo4j`
> 드라이버는 별도 추가가 필요 없다"고 적었으나, 위 이유로 **명시적 핀이 맞다.** 009 §8을 이에 맞게
> 수정했다.

### 2.5 포트/어댑터 — 009를 따른다

GraphRAG 쪽 파일 배치는 **[009-langgraph-strategy.md](009-langgraph-strategy.md) §7의 레이어 구성이
정본**이다. 이 문서에서 별도의 이름을 새로 만들지 않는다.

- `adapter/outbound/repositories/neo4j_document_graph_repository.py`가
  `grid_architect_graph_manager.get_driver_optional()`로 드라이버를 받아 세션을 연다.
  **`neo4j` 드라이버 세션을 여는 곳은 이 파일뿐이다**([002](002-neo4j-harness.md) §3).
- 드라이버가 `None`이면 어댑터 생성자에서 가드해 라우터를 비활성화하거나 503으로 변환한다.
- LangGraph 노드는 포트(`app/ports/output/`)만 의존한다([004](004-langgraph_harness.md) §3).

---

## 3. 검증 절차

```bash
# 1. 컨테이너 기동 후 healthy 확인
docker compose up -d neo4j
docker compose ps          # neo4j가 (healthy)로 표시되어야 한다

# 2. 브라우저 로그인 — http://localhost:7474 (neo4j / 루트 .env의 NEO4J_PASSWORD)

# 3. Bolt 레벨 접속 확인
docker compose exec neo4j cypher-shell -u neo4j -p "$NEO4J_PASSWORD" "RETURN 1"

# 4. 두 .env의 비밀번호가 같은지 확인 (§2.2의 함정)
#    루트 .env의 NEO4J_PASSWORD == minho/.env의 NEO4J_PASSWORD

# 5. 아키텍처 경계 재확인
cd minho && lint-imports
```

6. `grid_architect_graph_manager` 작성 후 FastAPI 기동 로그 확인 — **`NEO4J_URI`를 일부러 비운 채로도
   앱이 정상 기동하고 나머지 API가 살아 있어야 한다**(002 §4). 이 음성 케이스를 반드시 함께 확인한다.

---

## 4. 구현 순서

| # | 단계 | 검증 |
|---|------|------|
| 1 | `docker-compose.yaml`에 healthcheck + `NEO4J_PASSWORD` 추가 | `docker compose ps`에서 `healthy` |
| 2 | `backend.depends_on`을 매핑 형식으로 전환(`pgvector`·`redis` 누락 주의) | `docker compose config`로 파싱 확인 |
| 3 | `minho/.env.example`에 세 키 추가, `backend.environment`에 `NEO4J_URI` 추가 | 컨테이너 안 `env`에서 값 확인 |
| 4 | `minho/requirements.txt`에 `neo4j>=5.0,<6.0` 추가 | `pip install` 성공 |
| 5 | `core/matrix/grid_architect_graph_manager.py` 작성 | 미설정/정상 두 경우 모두 단위 테스트 |
| 6 | `main.py` lifespan에 `dispose_driver()` 연결 | 앱 기동·종료 로그 |
| 7 | 009 §7의 포트/어댑터 작성 | `lint-imports` + 009 체크리스트 |

1~4는 코드 변경이 없어 독립적으로 먼저 넣을 수 있다. 5부터가 실제 연결이다.

---

## 5. 완료 기준 체크리스트

- [ ] `neo4j` 서비스에 healthcheck가 있고 `docker compose ps`에서 `healthy`로 뜬다.
- [ ] `backend.depends_on`이 `neo4j: condition: service_healthy`이며, `pgvector`·`redis`가 누락되지 않았다.
- [ ] `minho/.env.example`에 `NEO4J_URI`/`NEO4J_USER`/`NEO4J_PASSWORD`가 주석과 함께 있다.
- [ ] `docker-compose.yaml`의 `backend.environment`에 `NEO4J_URI`가 있다.
- [ ] 루트 `.env`와 `minho/.env`의 `NEO4J_PASSWORD` 값이 같다.
- [ ] `minho/requirements.txt`에 `neo4j` 드라이버가 명시적으로 고정돼 있다.
- [ ] `grid_architect_graph_manager`가 `NEO4J_URI` 미설정 시 예외를 던지지 않고 `None`을 반환한다.
- [ ] **`NEO4J_URI`를 비운 채 앱을 기동해 나머지 API가 죽지 않는 것을 실제로 확인했다.**
- [ ] `main.py` lifespan에 `dispose_driver()`가 연결돼 있다.
- [ ] `neo4j` 드라이버 세션을 여는 곳이 `neo4j_document_graph_repository.py` 하나뿐이다([002](002-neo4j-harness.md) §3).
- [ ] `cd minho && lint-imports` 통과.

---

## 6. 참고

- [002-neo4j-harness.md](002-neo4j-harness.md) — 노드·라벨·관계 모델링 규칙, 연결 설정 원칙
- [004-langgraph_harness.md](004-langgraph_harness.md) — LangGraph 노드/엣지 규칙
- [009-langgraph-strategy.md](009-langgraph-strategy.md) — GraphRAG 전략, 레이어 구성 정본
- [`minho/_docs/architecture-star-topology.md`](../../../_docs/architecture-star-topology.md) — 허브/스포크 경계
