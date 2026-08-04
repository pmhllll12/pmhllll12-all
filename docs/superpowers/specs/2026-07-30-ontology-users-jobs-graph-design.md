# ontology users/jobs — pgvector 스키마와 Neo4j 그래프 설계

- 작성일: 2026-07-30
- 상태: 승인됨 (구현 계획 작성 대기)

## 목적

사용자와 직업을 잇는 최소 데이터셋을 두 저장소에 동시에 구축한다. pgvector에는
임베딩을 가진 관계형 테이블로, Neo4j에는 같은 데이터를 그래프로 적재해 두 저장소를
비교·활용할 수 있는 기반을 만든다.

범위는 데이터 구축까지다. 이 데이터를 소비하는 기능은 만들지 않는다.

## 결정 사항

| 항목 | 결정 | 근거 |
|---|---|---|
| 데이터 성격 | alembic으로 관리하는 정식 스키마 | 저장소의 모든 스키마 변경이 alembic을 거치고, 시드 데이터도 `20260713_0002_seed_moneyball_soccer_data.py` 선례가 있다 |
| 테이블 이름 | `ontology_users`, `ontology_jobs` | 11개 테이블 중 8개가 앱 접두어를 쓴다. 접두어 없는 `bookings`/`passengers`/`persons`는 레거시이고, `20260520_0002`에서 이미 한 번 접두어로 정리한 이력이 있다 |
| 코드 소유 앱 | `apps/ontology/` | 그래프·임베딩 성격의 `vision_analyzed_images`를 이미 소유한다 |
| 임베딩 | 두 테이블 모두 `vector(768)`, 마이그레이션은 NULL로 생성하고 별도 백필이 채운다 | `20260713_0001:108`이 `nullable=True`로 만들고 `player_embedding_backfill_interactor.py`가 나중에 채우는 기존 패턴 |
| 그래프 모델 | `(:User)-[:HAS_JOB]->(:Job)`, `company`는 Job 속성 | 요청한 두 테이블과 1:1 대응. 나중에 `(:Company)` 노드로 분리하려면 Cypher 한 문장이면 된다 |

## Postgres 스키마

```sql
ontology_users
  id        serial       PK
  name      varchar(50)  NOT NULL
  email     varchar(255) NOT NULL UNIQUE
  age       integer
  embedding vector(768)  NULL

ontology_jobs
  id        serial       PK
  title     varchar(100) NOT NULL
  company   varchar(100) NOT NULL
  userid    integer      NOT NULL REFERENCES ontology_users(id) ON DELETE CASCADE
  embedding vector(768)  NULL
```

컬럼 이름은 요청받은 그대로 둔다. `userid`는 저장소의 스네이크케이스 관례와
어긋나지만 명시적으로 지정된 이름이다.

`ontology_jobs.userid`에 인덱스를 만든다. FK 조회와 Neo4j 동기화가 이 컬럼으로
조인한다.

### 마이그레이션

현재 head는 `20260730_0001`이다. 두 개를 이어 붙인다.

1. `20260730_0002_create_ontology_users_jobs.py` — 테이블·FK·인덱스 생성
2. `20260730_0003_seed_ontology_users_jobs.py` — 시드 삽입

시드 INSERT문은 `apps/ontology/resources/users_jobs_seed_data.sql`에 두고
마이그레이션은 실행만 한다 (`20260713_0002`와 같은 구조).

`downgrade()`는 두 마이그레이션 모두 구현한다. 2번은 시드 행 삭제, 1번은 테이블
삭제다.

## 시드 데이터

`ontology_users` 5행과 `ontology_jobs` 5행을 1:1로 연결한다.

| id | name | email | age | job title | company |
|---|---|---|---|---|---|
| 1 | 김민준 | minjun.kim@example.com | 32 | 백엔드 개발자 | 카카오 |
| 2 | 이서연 | seoyeon.lee@example.com | 28 | 데이터 분석가 | 네이버 |
| 3 | 박도윤 | doyoon.park@example.com | 41 | 프로덕트 매니저 | 쿠팡 |
| 4 | 최지우 | jiwoo.choi@example.com | 26 | 프론트엔드 개발자 | 토스 |
| 5 | 정하은 | haeun.jung@example.com | 35 | 머신러닝 엔지니어 | 라인 |

이메일 도메인은 RFC 2606이 예약한 `example.com`을 쓴다. 실존 주소와 충돌하지
않는다.

두 테이블 모두 `id`가 serial이지만 시드는 명시적으로 1~5를 넣는다. 삽입 후
`ontology_users_id_seq`와 `ontology_jobs_id_seq`를 각각 `setval`로 5에 맞춘다.
그러지 않으면 이후 INSERT가 PK 충돌을 일으킨다.

## 스크립트 실행 환경

아래 두 스크립트는 모두 backend 컨테이너 안, 작업 디렉터리 `/app`에서 실행한다.

```
docker exec pmhllll12-all-backend-1 python apps/ontology/scripts/<파일명>.py
```

기존 `apps/ontology/scripts/run_classifier_sample.py`와 같은 호출 방식이다. 각
스크립트는 `sys.path`에 `/app`과 `/app/apps`를 직접 추가한다 — 컨테이너의
`sys.path`에 프로젝트 경로가 들어 있지 않아서, 이게 없으면 `database`와
`ontology` 모듈을 찾지 못한다.

그 컨테이너에만 `DATABASE_URL`, `GEMINI_API_KEY`, 그리고 추가할 `NEO4J_*`가
함께 있고 `neo4j` 드라이버도 설치돼 있다. 호스트에서 직접 실행하지 않는다.

## 임베딩 백필

`apps/ontology/scripts/backfill_users_jobs_embedding.py`

마이그레이션과 분리한다. 마이그레이션 안에서 외부 API를 호출하면 오프라인 배포와
재실행이 깨진다.

- 임베딩 텍스트: user는 `"{name} {age}세"`, job은 `"{title} {company}"`
- 호출: `core.matrix.vault_keymaker_secret_manager.keymaker.embed_content()`
  (모델 `models/gemini-embedding-001`, `EMBEDDING_DIM = 768`)
- `embedding IS NULL`인 행만 처리한다. 재실행해도 중복 호출이 없다.
- 총 호출 10건 (users 5 + jobs 5)

### 아키텍처 제약

`pyproject.toml`의 import-linter contract 2는 `ontology`가 스포크
(`titanic`/`community`/`moneyball` 등)를 import하는 것을 금지한다. 따라서
`community/adapter/outbound/gemini_embedding_client.py`를 재사용할 수 없고,
`ontology` 안에 같은 패턴의 어댑터를 따로 둔다.

`core.matrix`는 `ontology`와 같은 그래프 최하단이므로 참조해도 된다.

## Neo4j 동기화

`apps/ontology/scripts/sync_users_jobs_to_neo4j.py`

Postgres를 읽어 Cypher로 적재한다. 단방향이다 — Postgres가 정본이고 Neo4j는
파생이다.

```cypher
CREATE CONSTRAINT user_id_unique IF NOT EXISTS
  FOR (u:User) REQUIRE u.id IS UNIQUE;
CREATE CONSTRAINT job_id_unique IF NOT EXISTS
  FOR (j:Job)  REQUIRE j.id IS UNIQUE;

MERGE (u:User {id: $id}) SET u.name = $name, u.email = $email, u.age = $age;
MERGE (j:Job  {id: $id}) SET j.title = $title, j.company = $company;

MATCH (u:User {id: $userid}), (j:Job {id: $jobid})
MERGE (u)-[:HAS_JOB]->(j);
```

`MERGE`와 uniqueness constraint를 함께 쓰므로 몇 번 실행해도 노드와 관계가
중복되지 않는다.

임베딩 벡터는 Neo4j로 보내지 않는다. 벡터 검색은 pgvector가 담당한다.

## 설정 변경

backend 컨테이너에 `NEO4J_*` 환경변수가 하나도 없다. `docker-compose.yaml`의
backend `environment:`에 추가한다.

```yaml
NEO4J_URI: bolt://neo4j:7687
NEO4J_USER: neo4j
NEO4J_PASSWORD: ${NEO4J_PASSWORD}
```

루트 `.env`의 `NEO4J_PASSWORD`로 접속되는 것은 확인했다 (Neo4j 5.26.28).
드라이버 `neo4j 6.2.0`은 backend에 이미 설치돼 있다 (`neo4j-graphrag`의 의존성).

## 오류 처리

| 상황 | 처리 |
|---|---|
| 백필 중 Gemini 호출 실패 | 해당 행을 건너뛰고 로그를 남긴 뒤 계속한다. 남은 NULL은 재실행으로 채운다 |
| 백필이 반환한 벡터 차원이 768이 아님 | 저장하지 않고 실패로 기록한다. 잘못된 차원은 INSERT 시점에 에러가 나므로 미리 막는다 |
| Neo4j 접속 실패 | 스크립트를 비정상 종료 코드로 끝낸다. Postgres는 이미 정본이라 부분 적재만 남고, 재실행이 멱등이므로 복구된다 |
| 시드 재실행 | 마이그레이션은 alembic이 한 번만 실행한다. 수동 재실행 시 PK 충돌로 실패하는 것이 맞는 동작이다 |

## 검증

| 대상 | 확인 |
|---|---|
| 마이그레이션 | `alembic upgrade head` 후 `alembic current`가 `20260730_0003` |
| 되돌리기 | `alembic downgrade 20260730_0001` 후 두 테이블이 사라짐 |
| 시드 | `ontology_users` 5행, `ontology_jobs` 5행, FK 무결성 위반 0 |
| 백필 | 두 테이블 모두 `embedding IS NOT NULL` 5행, `vector_dims(embedding) = 768` |
| 그래프 | `User` 5, `Job` 5, `HAS_JOB` 5 |
| 멱등성 | 동기화 스크립트를 2회 실행해도 위 숫자가 그대로 |
| 회귀 | `pytest`, `lint-imports`, `ruff` |

## 범위 밖

API 엔드포인트, 유사도 검색 기능, Neo4j 벡터 인덱스, 프런트엔드 화면은 만들지
않는다. Neo4j에서 Postgres로 되돌리는 역방향 동기화도 하지 않는다.
