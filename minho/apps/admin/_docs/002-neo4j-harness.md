# NEO4J-HARNESS.md

`apps/admin`에서 그래프 데이터(Neo4j)를 다룰 때 지키는 모델링·운영 규칙. 인프라(`docker-compose.yaml`의 `neo4j` 서비스)와 라이브러리(`requirements.txt`의 `neo4j-graphrag`)는 이미 준비되어 있고, 이 문서는 **그 위에서 그래프를 어떻게 설계·구현할지**를 정한다.

---

## 0. 컨텍스트

- Neo4j 컨테이너: `docker-compose.yaml`의 `neo4j` 서비스(`neo4j:5-community`, Bolt `7687`, 브라우저 `7474`).
- 인증: `NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}` — 사용자명은 `neo4j` 고정, 비밀번호는 루트 `.env`의 `NEO4J_PASSWORD`.
- 드라이버/도구: `minho/requirements.txt`의 `neo4j-graphrag==1.18.0`(내부에 `neo4j` 공식 드라이버 포함).
- `backend` 서비스는 `depends_on: [neo4j]`까지만 되어 있고 `NEO4J_URI`/`NEO4J_USER`/`NEO4J_PASSWORD` 환경변수는 아직 주입되지 않는다 — 연결 코드를 작성하는 시점에 `docker-compose.yaml`의 `backend.environment`와 `minho/.env.example`에 추가한다(§4).

---

## 1. 그래프 데이터 모델 기본 개념

그래프 데이터는 **노드(node)**, **라벨(label)**, **관계(relationship)**, **속성(property)** 네 가지로 정의되며, 노드와 관계가 그래프를 구성하는 기본 단위다.

- **노드(node)**: 그래프에서 동그라미로 표현되는 개별 개체. 노드 하나가 엔티티 하나를 식별한다.
- **라벨(label)**: 노드에 붙는 분류표(예: `Person`, `Book`). 같은 라벨을 가진 노드들은 같은 종류의 엔티티로 취급한다. 노드 하나가 라벨을 여러 개 가질 수도 있다.
- **관계(relationship)**: 두 노드를 연결하는 화살표. 방향과 타입을 가진다(예: 사람이 책을 "읽었다"는 `:HAS_READ`, 두 사람이 "친구다"는 `:IS_FRIENDS_WITH`). 관계는 항상 시작 노드 → 끝 노드 방향을 가지며, 조회 시 방향을 무시할 수도 있다.
- **속성(property)**: 노드나 관계에 붙는 키-값 설명. `Person` 노드는 `name`, `age` 속성을 가질 수 있고, `:HAS_READ` 관계는 언제 읽었는지를 나타내는 `on` 같은 속성을 가질 수 있다. 속성은 노드/관계를 식별·필터링하는 데 쓰인다.

---

## 2. 이 저장소의 표기 규칙

| 요소 | 표기 | 예 |
|------|------|-----|
| 라벨 | PascalCase, 단수형 | `Person`, `Book`, `Employee` |
| 관계 타입 | SCREAMING_SNAKE_CASE, 콜론 접두, 동사(구) | `:HAS_READ`, `:IS_FRIENDS_WITH`, `:REPORTS_TO` |
| 속성 키 | snake_case | `name`, `created_at`, `read_on` |
| 식별자 속성 | 엔티티마다 고유 속성 하나를 `id`로 통일(가능하면 기존 Postgres PK 재사용) | `Person.id`, `Book.id` |

- 관계는 항상 의미상 능동태로 이름 붙인다(`:HAS_READ`이지 `:READ_BY`가 아님). 역방향 조회는 Cypher 패턴의 화살표 방향만 바꿔서 처리하고, 반대 의미의 관계 타입을 별도로 만들지 않는다.
- 하나의 관계 타입은 하나의 의미만 가진다 — 여러 의미를 담고 싶으면 관계를 나누거나 속성으로 구분한다(타입 문자열로 분기하지 않는다).
- 라벨·관계·속성 이름은 영문으로 통일한다(한글 라벨/속성 키 금지) — Cypher 쿼리와 코드 전반의 일관성을 위함.

---

## 3. 헥사고날 계층에서의 위치

`minho/_docs/architecture-star-topology.md`가 정한 `domain → app → adapter` 경계를 그래프 데이터에도 그대로 적용한다.

- `domain/`: 노드·관계를 순수 파이썬 엔티티/값 객체로 표현(예: `PersonNode`, `HasReadRelationship`). Cypher나 `neo4j` 드라이버를 import하지 않는다.
- `app/ports/output/`: 그래프 저장소 포트(예: `GraphRepositoryPort`)를 인터페이스로 정의. 유스케이스는 이 포트만 의존한다.
- `adapter/outbound/repositories/`: 포트 구현체가 실제 Cypher를 실행한다. `neo4j.AsyncGraphDatabase` 드라이버 세션은 이 계층에만 존재해야 한다(다른 앱이 직접 열지 않는다 — 스타 토폴로지의 스포크 간 금지 규칙과 동일한 이유).
- Cypher 쿼리 문자열은 리터럴로 adapter 파일에 두고, 파라미터는 반드시 바인딩 파라미터(`$name` 등)로 넘긴다 — f-string으로 값을 쿼리에 직접 삽입하지 않는다(인젝션 방지, `database.py`의 SQLAlchemy 파라미터 바인딩과 동일 원칙).

---

## 4. 연결 설정

`database.py`(Postgres)와 동일하게, 연결 정보는 환경변수로만 받고 모듈 로드 시점이 아니라 세션 생성 시점에 읽는다.

```
NEO4J_URI=bolt://neo4j:7687        # 로컬: bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<.env의 NEO4J_PASSWORD와 동일>
```

- `minho/.env.example`에 위 세 키를 주석과 함께 추가한다.
- `docker-compose.yaml`의 `backend.environment`에 `NEO4J_URI: bolt://neo4j:7687`을 추가하고, `NEO4J_PASSWORD`는 `env_file`(`./minho/.env`)로 주입한다 — 루트 `.env`의 `NEO4J_PASSWORD`와 값이 같아야 `neo4j` 컨테이너 인증을 통과한다.
- Neon Postgres가 미설정이어도 API 일부만 죽는 `database.py`의 패턴처럼, `NEO4J_URI` 미설정 시 그래프 관련 라우터만 비활성화하고 나머지 API는 정상 기동해야 한다(그래프 어댑터 생성자에서 `None` 가드).

---

## 5. 스키마 제약·인덱스

- 각 라벨의 식별자 속성(`id`)에는 유니크 제약을 건다:
  ```cypher
  CREATE CONSTRAINT person_id_unique IF NOT EXISTS
  FOR (p:Person) REQUIRE p.id IS UNIQUE;
  ```
- 제약/인덱스 생성 Cypher는 코드에 하드코딩하지 않고, `alembic/`처럼 버전 관리되는 마이그레이션 스크립트(예: `apps/admin/adapter/outbound/graph_migrations/`)로 분리해 재실행 가능(idempotent, `IF NOT EXISTS`)하게 작성한다.
- 노드 병합은 `MERGE`를 쓰되 항상 식별자 속성만으로 매칭한다(`MERGE (p:Person {id: $id})`) — 이름 등 가변 속성으로 `MERGE`하면 중복 노드가 생긴다.

---

## 6. 완료 기준 체크리스트

- [ ] `minho/.env.example`에 `NEO4J_URI`/`NEO4J_USER`/`NEO4J_PASSWORD` 추가.
- [ ] `docker-compose.yaml`의 `backend.environment`에 `NEO4J_URI` 추가.
- [ ] `domain/`에 Cypher·드라이버 import 없음(순수 엔티티만).
- [ ] `adapter/outbound/`에서만 `neo4j` 드라이버 세션을 연다.
- [ ] 모든 Cypher 쿼리가 바인딩 파라미터를 쓰고 f-string 삽입이 없다.
- [ ] 식별자 속성에 대한 유니크 제약이 마이그레이션 스크립트로 존재한다.
- [ ] `NEO4J_URI` 미설정 시 나머지 API가 죽지 않는다.
