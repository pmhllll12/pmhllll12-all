# ontology users/jobs — pgvector 스키마와 Neo4j 그래프 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `ontology_users`/`ontology_jobs` 테이블을 임베딩 컬럼과 함께 만들고 한글 더미 5건을 넣은 뒤, 같은 데이터를 Neo4j에 `(:User)-[:HAS_JOB]->(:Job)` 그래프로 적재한다.

**Architecture:** Postgres가 정본이고 Neo4j는 파생이다. 스키마와 시드는 alembic 마이그레이션 2개로 만들고, 외부 API를 부르는 임베딩 백필과 Neo4j 적재는 마이그레이션 밖의 독립 스크립트로 분리한다. 두 스크립트 모두 재실행이 안전하다.

**Tech Stack:** SQLAlchemy 2.0 (async, `Mapped`/`mapped_column`), alembic, pgvector 0.8 (`pgvector.sqlalchemy.Vector`), neo4j 파이썬 드라이버 6.2.0, Gemini 임베딩(`core.matrix.vault_keymaker_secret_manager.keymaker`), pytest.

## Global Constraints

- 임베딩 차원은 **768**이다. 상수는 `core.matrix.vault_keymaker_secret_manager.EMBEDDING_DIM`에 있다.
- 테이블 이름은 **`ontology_users`**, **`ontology_jobs`**로 고정한다.
- 컬럼 이름은 **`id, name, email, age`** / **`id, title, company, userid`**로 고정한다. `userid`는 스네이크케이스가 아니지만 의도된 이름이다.
- **마이그레이션 안에서 외부 API를 호출하지 않는다.**
- `import-linter` contract 2: `ontology`는 `titanic`/`soccer`/`social_network`/`matching`/`admin`/`moneyball`/`community`/`sample`을 import할 수 없다. `core`/`matrix`/`adapters`는 참조해도 된다.
- 현재 alembic head는 **`20260730_0001`**이다. 새 리비전은 여기서 이어 붙인다.
- 모든 스크립트는 backend 컨테이너 안, 작업 디렉터리 `/app`에서 실행한다.
- 커밋 메시지는 Conventional Commits + 한국어, 제목 50자 이내다.

---

### Task 1: ORM 모델과 테이블 생성 마이그레이션

**Files:**
- Create: `minho/apps/ontology/adapter/outbound/orm/user_orm.py`
- Create: `minho/apps/ontology/adapter/outbound/orm/job_orm.py`
- Create: `minho/alembic/versions/20260730_0002_create_ontology_users_jobs.py`
- Modify: `minho/database.py:173` (`create_all_tables()`의 ontology import 줄)
- Test: `minho/apps/ontology/tests/adapter/outbound/orm/test_users_jobs_orm.py`

**Interfaces:**
- Consumes: `database.Base`, `core.matrix.vault_keymaker_secret_manager.EMBEDDING_DIM`
- Produces: `ontology.adapter.outbound.orm.user_orm.UserOrm`(`id: int`, `name: str`, `email: str`, `age: int | None`, `embedding: list[float] | None`, `jobs: list[JobOrm]`), `ontology.adapter.outbound.orm.job_orm.JobOrm`(`id: int`, `title: str`, `company: str`, `userid: int`, `embedding: list[float] | None`, `user: UserOrm`). 리비전 `20260730_0002`.

- [ ] **Step 1: 테스트 디렉터리 패키지 파일 생성**

```bash
cd /home/ec2-user/pmhllll12-all/minho
mkdir -p apps/ontology/tests/adapter/outbound/orm
touch apps/ontology/tests/adapter/outbound/orm/__init__.py
ls apps/ontology/adapter/outbound/orm/__init__.py
```

`apps/ontology/adapter/outbound/orm/__init__.py`가 이미 있는지 확인한다. 없으면 빈 파일로 만든다.

- [ ] **Step 2: 실패하는 테스트 작성**

`minho/apps/ontology/tests/adapter/outbound/orm/test_users_jobs_orm.py`:

```python
from __future__ import annotations

from ontology.adapter.outbound.orm.job_orm import JobOrm
from ontology.adapter.outbound.orm.user_orm import UserOrm


def test_user_table_name_and_columns():
    assert UserOrm.__tablename__ == "ontology_users"
    columns = UserOrm.__table__.columns
    assert set(columns.keys()) == {"id", "name", "email", "age", "embedding"}
    assert columns["id"].primary_key is True
    assert columns["email"].unique is True
    assert columns["name"].nullable is False
    assert columns["age"].nullable is True


def test_job_table_name_and_columns():
    assert JobOrm.__tablename__ == "ontology_jobs"
    columns = JobOrm.__table__.columns
    assert set(columns.keys()) == {"id", "title", "company", "userid", "embedding"}
    assert columns["userid"].nullable is False


def test_job_userid_is_fk_to_users_with_cascade():
    fk = next(iter(JobOrm.__table__.columns["userid"].foreign_keys))
    assert fk.column.table.name == "ontology_users"
    assert fk.column.name == "id"
    assert fk.ondelete == "CASCADE"


def test_embedding_columns_are_768_dim_and_nullable():
    for orm in (UserOrm, JobOrm):
        column = orm.__table__.columns["embedding"]
        assert column.nullable is True
        assert column.type.dim == 768
```

- [ ] **Step 3: 테스트가 실패하는지 확인**

Run: `cd /home/ec2-user/pmhllll12-all/minho && python -m pytest apps/ontology/tests/adapter/outbound/orm/test_users_jobs_orm.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'ontology.adapter.outbound.orm.user_orm'`

- [ ] **Step 4: `UserOrm` 작성**

`minho/apps/ontology/adapter/outbound/orm/user_orm.py`:

```python
"""ontology_users — 사용자 엔티티 (pgvector 임베딩 컬럼 포함)."""

from __future__ import annotations

from database import Base
from pgvector.sqlalchemy import Vector
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

EMBEDDING_DIM = 768


class UserOrm(Base):
    __tablename__ = "ontology_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)

    jobs: Mapped[list["JobOrm"]] = relationship(  # noqa: F821
        back_populates="user", cascade="all, delete-orphan"
    )
```

`EMBEDDING_DIM`을 여기서 다시 선언하는 것은 `moneyball/adapter/outbound/orm/player_orm.py:11`과 같은 방식이다. ORM이 `core.matrix`(Gemini 설정을 들고 있음)를 import하지 않게 하려는 의도다.

- [ ] **Step 5: `JobOrm` 작성**

`minho/apps/ontology/adapter/outbound/orm/job_orm.py`:

```python
"""ontology_jobs — 직업 엔티티. userid 가 ontology_users.id 를 참조한다."""

from __future__ import annotations

from database import Base
from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ontology.adapter.outbound.orm.user_orm import UserOrm

EMBEDDING_DIM = 768


class JobOrm(Base):
    __tablename__ = "ontology_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    company: Mapped[str] = mapped_column(String(100), nullable=False)
    userid: Mapped[int] = mapped_column(
        Integer, ForeignKey("ontology_users.id", ondelete="CASCADE"), nullable=False
    )
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM), nullable=True)

    user: Mapped[UserOrm] = relationship(back_populates="jobs")
```

- [ ] **Step 6: 테스트가 통과하는지 확인**

Run: `cd /home/ec2-user/pmhllll12-all/minho && python -m pytest apps/ontology/tests/adapter/outbound/orm/test_users_jobs_orm.py -v`
Expected: PASS (4 passed)

- [ ] **Step 7: `create_all_tables()`에 모델 등록**

`minho/database.py`의 173번 줄을 다음으로 바꾼다:

```python
    from ontology.adapter.outbound.orm import job_orm, user_orm, vision_orm  # noqa: F401
```

- [ ] **Step 8: 테이블 생성 마이그레이션 작성**

`minho/alembic/versions/20260730_0002_create_ontology_users_jobs.py`:

```python
"""ontology_users / ontology_jobs 테이블 생성 (pgvector 임베딩 컬럼 포함).

Revision ID: 20260730_0002
Revises: 20260730_0001
Create Date: 2026-07-30
"""

from __future__ import annotations

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy import inspect

from alembic import op

revision = "20260730_0002"
down_revision = "20260730_0001"
branch_labels = None
depends_on = None

_EMBEDDING_DIM = 768


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())

    if "ontology_users" not in tables:
        op.create_table(
            "ontology_users",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("name", sa.String(length=50), nullable=False),
            sa.Column("email", sa.String(length=255), nullable=False, unique=True),
            sa.Column("age", sa.Integer(), nullable=True),
            sa.Column("embedding", Vector(_EMBEDDING_DIM), nullable=True),
        )

    if "ontology_jobs" not in tables:
        op.create_table(
            "ontology_jobs",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("title", sa.String(length=100), nullable=False),
            sa.Column("company", sa.String(length=100), nullable=False),
            sa.Column(
                "userid",
                sa.Integer(),
                sa.ForeignKey("ontology_users.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("embedding", Vector(_EMBEDDING_DIM), nullable=True),
        )
        op.create_index("ix_ontology_jobs_userid", "ontology_jobs", ["userid"])


def downgrade() -> None:
    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())

    if "ontology_jobs" in tables:
        op.drop_index("ix_ontology_jobs_userid", table_name="ontology_jobs")
        op.drop_table("ontology_jobs")
    if "ontology_users" in tables:
        op.drop_table("ontology_users")
```

- [ ] **Step 9: 마이그레이션 적용**

```bash
docker exec pmhllll12-all-backend-1 alembic upgrade head
docker exec pmhllll12-all-backend-1 alembic current
```

Expected: `20260730_0002 (head)`

- [ ] **Step 10: 실제 스키마 검증**

```bash
docker exec pmhllll12-all-pgvector-1 psql -U postgres -d neondb -c "\d ontology_users"
docker exec pmhllll12-all-pgvector-1 psql -U postgres -d neondb -c "\d ontology_jobs"
```

Expected: `embedding | vector(768)` 두 테이블 모두, `ontology_jobs.userid`에 FK와 인덱스 `ix_ontology_jobs_userid`.

- [ ] **Step 11: 되돌리기 검증 후 재적용**

```bash
docker exec pmhllll12-all-backend-1 alembic downgrade 20260730_0001
docker exec pmhllll12-all-pgvector-1 psql -U postgres -d neondb -tAc \
  "select count(*) from information_schema.tables where table_name like 'ontology_%'"
docker exec pmhllll12-all-backend-1 alembic upgrade head
```

Expected: downgrade 후 `0`, 그 뒤 upgrade가 오류 없이 끝난다.

- [ ] **Step 12: 커밋**

```bash
cd /home/ec2-user/pmhllll12-all
git add minho/apps/ontology/adapter/outbound/orm/user_orm.py \
        minho/apps/ontology/adapter/outbound/orm/job_orm.py \
        minho/apps/ontology/tests/adapter/outbound/orm/ \
        minho/alembic/versions/20260730_0002_create_ontology_users_jobs.py \
        minho/database.py
git commit -m "feat: ontology_users/ontology_jobs 테이블과 ORM 추가"
```

---

### Task 2: 한글 시드 데이터

**Files:**
- Create: `minho/apps/ontology/resources/users_jobs_seed_data.sql`
- Create: `minho/alembic/versions/20260730_0003_seed_ontology_users_jobs.py`
- Test: `minho/apps/ontology/tests/adapter/outbound/orm/test_users_jobs_seed_sql.py`

**Interfaces:**
- Consumes: Task 1의 `ontology_users`/`ontology_jobs` 테이블, 리비전 `20260730_0002`
- Produces: 리비전 `20260730_0003`. `ontology_users` 5행(id 1~5), `ontology_jobs` 5행(id 1~5, userid 1~5).

- [ ] **Step 1: resources 디렉터리 확인**

```bash
cd /home/ec2-user/pmhllll12-all/minho
mkdir -p apps/ontology/resources
```

- [ ] **Step 2: 실패하는 테스트 작성**

`minho/apps/ontology/tests/adapter/outbound/orm/test_users_jobs_seed_sql.py`:

```python
from __future__ import annotations

from pathlib import Path

_SEED_FILE = (
    Path(__file__).resolve().parents[4] / "resources" / "users_jobs_seed_data.sql"
)


def test_seed_file_exists():
    assert _SEED_FILE.is_file()


def test_seed_has_five_users_and_five_jobs():
    sql = _SEED_FILE.read_text(encoding="utf-8")
    assert sql.count("INSERT INTO ontology_users") == 1
    assert sql.count("INSERT INTO ontology_jobs") == 1
    # 각 INSERT 의 VALUES 행 수 = 5
    users_block = sql.split("INSERT INTO ontology_users")[1].split(";")[0]
    jobs_block = sql.split("INSERT INTO ontology_jobs")[1].split(";")[0]
    assert users_block.count("(") - users_block.count("(id") == 5
    assert jobs_block.count("(") - jobs_block.count("(id") == 5


def test_seed_uses_reserved_example_domain():
    sql = _SEED_FILE.read_text(encoding="utf-8")
    assert sql.count("@example.com") == 5


def test_seed_resets_both_sequences():
    sql = _SEED_FILE.read_text(encoding="utf-8")
    assert "ontology_users_id_seq" in sql
    assert "ontology_jobs_id_seq" in sql
```

`parents[4]`는 `tests/adapter/outbound/orm/` 4단계를 올라가 `apps/ontology/`에 닿는다.

- [ ] **Step 3: 테스트가 실패하는지 확인**

Run: `cd /home/ec2-user/pmhllll12-all/minho && python -m pytest apps/ontology/tests/adapter/outbound/orm/test_users_jobs_seed_sql.py -v`
Expected: FAIL — `assert False` (파일 없음)

- [ ] **Step 4: 시드 SQL 작성**

`minho/apps/ontology/resources/users_jobs_seed_data.sql`:

```sql
-- ontology_users / ontology_jobs 더미 데이터 5건.
-- 이메일 도메인은 RFC 2606 이 예약한 example.com 을 쓴다 (실존 주소와 충돌 방지).
-- embedding 은 여기서 채우지 않는다 — scripts/backfill_users_jobs_embedding.py 담당.

INSERT INTO ontology_users (id, name, email, age) VALUES
    (1, '김민준', 'minjun.kim@example.com', 32),
    (2, '이서연', 'seoyeon.lee@example.com', 28),
    (3, '박도윤', 'doyoon.park@example.com', 41),
    (4, '최지우', 'jiwoo.choi@example.com', 26),
    (5, '정하은', 'haeun.jung@example.com', 35);

INSERT INTO ontology_jobs (id, title, company, userid) VALUES
    (1, '백엔드 개발자', '카카오', 1),
    (2, '데이터 분석가', '네이버', 2),
    (3, '프로덕트 매니저', '쿠팡', 3),
    (4, '프론트엔드 개발자', '토스', 4),
    (5, '머신러닝 엔지니어', '라인', 5);

-- id 를 명시 삽입했으므로 시퀀스를 마지막 값에 맞춘다.
-- 그러지 않으면 이후 INSERT 가 PK 충돌을 일으킨다.
SELECT setval('ontology_users_id_seq', 5, true);
SELECT setval('ontology_jobs_id_seq', 5, true);
```

- [ ] **Step 5: 테스트가 통과하는지 확인**

Run: `cd /home/ec2-user/pmhllll12-all/minho && python -m pytest apps/ontology/tests/adapter/outbound/orm/test_users_jobs_seed_sql.py -v`
Expected: PASS (4 passed)

- [ ] **Step 6: 시드 마이그레이션 작성**

`minho/alembic/versions/20260730_0003_seed_ontology_users_jobs.py`:

```python
"""ontology_users / ontology_jobs 시드 데이터 적재.

`apps/ontology/resources/users_jobs_seed_data.sql` 의 문장을 그대로 실행한다.
이미 데이터가 있으면 건너뛴다.

Revision ID: 20260730_0003
Revises: 20260730_0002
Create Date: 2026-07-30
"""

from __future__ import annotations

from pathlib import Path

import sqlalchemy as sa

from alembic import op

revision = "20260730_0003"
down_revision = "20260730_0002"
branch_labels = None
depends_on = None

_ONTOLOGY_APP_ROOT = Path(__file__).resolve().parents[2] / "apps" / "ontology"
_SEED_FILE = _ONTOLOGY_APP_ROOT / "resources" / "users_jobs_seed_data.sql"


def upgrade() -> None:
    bind = op.get_bind()
    already_seeded = bind.execute(sa.text("SELECT count(*) FROM ontology_users")).scalar_one()
    if already_seeded:
        return

    sql_text = _SEED_FILE.read_text(encoding="utf-8")
    for chunk in sql_text.split(";"):
        statement = "\n".join(
            line for line in chunk.splitlines() if not line.strip().startswith("--")
        ).strip()
        if not statement or statement.upper() == "COMMIT":
            continue
        op.execute(statement)


def downgrade() -> None:
    bind = op.get_bind()
    # ontology_jobs 가 CASCADE FK 라 users 만 지워도 되지만, 명시적으로 둘 다 지운다.
    for table in ("ontology_jobs", "ontology_users"):
        bind.execute(sa.text(f"DELETE FROM {table}"))
    for sequence in ("ontology_jobs_id_seq", "ontology_users_id_seq"):
        bind.execute(sa.text(f"SELECT setval('{sequence}', 1, false)"))
```

`_SEED_FILE` 경로 계산은 `20260713_0002_seed_moneyball_soccer_data.py:24`와 같은 방식이다 (`versions/` → `alembic/` → `minho/`).

- [ ] **Step 7: 마이그레이션 적용**

```bash
docker exec pmhllll12-all-backend-1 alembic upgrade head
docker exec pmhllll12-all-backend-1 alembic current
```

Expected: `20260730_0003 (head)`

- [ ] **Step 8: 데이터와 FK 무결성 검증**

```bash
docker exec pmhllll12-all-pgvector-1 psql -U postgres -d neondb -c "
select u.id, u.name, u.email, u.age, j.title, j.company
from ontology_users u join ontology_jobs j on j.userid = u.id
order by u.id;"
```

Expected: 5행. 한글이 깨지지 않고 `김민준 … 백엔드 개발자 카카오`부터 출력된다.

```bash
docker exec pmhllll12-all-pgvector-1 psql -U postgres -d neondb -tAc "
select (select count(*) from ontology_users) || '/' ||
       (select count(*) from ontology_jobs)  || '/' ||
       (select count(*) from ontology_jobs j
          left join ontology_users u on u.id = j.userid where u.id is null);"
```

Expected: `5/5/0` (users 5, jobs 5, 고아 FK 0)

- [ ] **Step 9: 시퀀스가 맞춰졌는지 검증**

```bash
docker exec pmhllll12-all-pgvector-1 psql -U postgres -d neondb -tAc "
select last_value from ontology_users_id_seq;
select last_value from ontology_jobs_id_seq;"
```

Expected: 둘 다 `5`

- [ ] **Step 10: 커밋**

```bash
cd /home/ec2-user/pmhllll12-all
git add minho/apps/ontology/resources/users_jobs_seed_data.sql \
        minho/alembic/versions/20260730_0003_seed_ontology_users_jobs.py \
        minho/apps/ontology/tests/adapter/outbound/orm/test_users_jobs_seed_sql.py
git commit -m "feat: ontology users/jobs 한글 더미 5건 시드 추가"
```

---

### Task 3: 임베딩 백필

**Files:**
- Create: `minho/apps/ontology/app/ports/output/embedding_port.py`
- Create: `minho/apps/ontology/adapter/outbound/gemini_embedding_client.py`
- Create: `minho/apps/ontology/app/use_cases/users_jobs_embedding_backfill.py`
- Create: `minho/apps/ontology/scripts/backfill_users_jobs_embedding.py`
- Test: `minho/apps/ontology/tests/app/use_cases/test_users_jobs_embedding_backfill.py`

**Interfaces:**
- Consumes: Task 1의 `UserOrm`/`JobOrm`, `core.matrix.vault_keymaker_secret_manager.keymaker`
- Produces: `EmbeddingPort.embed(text: str) -> list[float]`; `build_user_text(name: str, age: int | None) -> str`; `build_job_text(title: str, company: str) -> str`; `backfill_rows(rows: Sequence[tuple[int, str]], embedder: EmbeddingPort, save: Callable[[int, list[float]], Awaitable[None]], dim: int = 768) -> BackfillResult`(`filled: int`, `failed: int`)

- [ ] **Step 1: 임베딩 포트 작성**

`minho/apps/ontology/app/ports/output/embedding_port.py`:

```python
"""텍스트 → 벡터 변환 포트. community 앱의 동명 포트를 재사용할 수 없다 —
import-linter contract 2 가 ontology → community 를 금지한다."""

from __future__ import annotations

from typing import Protocol


class EmbeddingPort(Protocol):
    async def embed(self, text: str) -> list[float]: ...
```

- [ ] **Step 2: 실패하는 테스트 작성**

`minho/apps/ontology/tests/app/use_cases/test_users_jobs_embedding_backfill.py`:

```python
from __future__ import annotations

import asyncio

from ontology.app.use_cases.users_jobs_embedding_backfill import (
    backfill_rows,
    build_job_text,
    build_user_text,
)


class _FakeEmbedder:
    def __init__(self, dim: int = 768, fail_on: str | None = None):
        self.dim = dim
        self.fail_on = fail_on
        self.calls: list[str] = []

    async def embed(self, text: str) -> list[float]:
        self.calls.append(text)
        if self.fail_on is not None and self.fail_on in text:
            raise RuntimeError("embed 실패")
        return [0.1] * self.dim


def test_build_user_text_includes_name_and_age():
    assert build_user_text("김민준", 32) == "김민준 32세"


def test_build_user_text_without_age():
    assert build_user_text("김민준", None) == "김민준"


def test_build_job_text_joins_title_and_company():
    assert build_job_text("백엔드 개발자", "카카오") == "백엔드 개발자 카카오"


def test_backfill_fills_every_row():
    embedder = _FakeEmbedder()
    rows = [(1, "김민준 32세"), (2, "이서연 28세")]
    saved: dict[int, list[float]] = {}

    async def save(row_id, vector):
        saved[row_id] = vector

    result = asyncio.run(backfill_rows(rows, embedder, save))

    assert result.filled == 2
    assert result.failed == 0
    assert len(saved[1]) == 768
    assert embedder.calls == ["김민준 32세", "이서연 28세"]


def test_backfill_skips_row_whose_embed_fails_and_continues():
    embedder = _FakeEmbedder(fail_on="이서연")
    rows = [(1, "김민준 32세"), (2, "이서연 28세"), (3, "박도윤 41세")]
    saved: dict[int, list[float]] = {}

    async def save(row_id, vector):
        saved[row_id] = vector

    result = asyncio.run(backfill_rows(rows, embedder, save))

    assert result.filled == 2
    assert result.failed == 1
    assert set(saved) == {1, 3}


def test_backfill_rejects_wrong_dimension_vector():
    embedder = _FakeEmbedder(dim=512)
    rows = [(1, "김민준 32세")]
    saved: dict[int, list[float]] = {}

    async def save(row_id, vector):
        saved[row_id] = vector

    result = asyncio.run(backfill_rows(rows, embedder, save))

    assert result.filled == 0
    assert result.failed == 1
    assert saved == {}
```

- [ ] **Step 3: 테스트가 실패하는지 확인**

Run: `cd /home/ec2-user/pmhllll12-all/minho && python -m pytest apps/ontology/tests/app/use_cases/test_users_jobs_embedding_backfill.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'ontology.app.use_cases.users_jobs_embedding_backfill'`

- [ ] **Step 4: 백필 유스케이스 작성**

`minho/apps/ontology/app/use_cases/users_jobs_embedding_backfill.py`:

```python
"""ontology_users / ontology_jobs 의 embedding 컬럼 백필 로직 (순수 함수).

DB·Gemini 접근은 호출자가 주입한다. 그래야 테스트가 외부 의존 없이 돈다.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass

from ontology.app.ports.output.embedding_port import EmbeddingPort

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 768


@dataclass(frozen=True)
class BackfillResult:
    filled: int = 0
    failed: int = 0


def build_user_text(name: str, age: int | None) -> str:
    """사용자 임베딩용 텍스트. 나이가 없으면 이름만 쓴다."""
    if age is None:
        return name
    return f"{name} {age}세"


def build_job_text(title: str, company: str) -> str:
    return f"{title} {company}"


async def backfill_rows(
    rows: Sequence[tuple[int, str]],
    embedder: EmbeddingPort,
    save: Callable[[int, list[float]], Awaitable[None]],
    dim: int = EMBEDDING_DIM,
) -> BackfillResult:
    """(id, 텍스트) 목록을 임베딩해 저장한다.

    한 행이 실패해도 나머지를 계속 처리한다 — 남은 NULL 은 재실행으로 채운다.
    """
    filled = failed = 0

    for row_id, text in rows:
        try:
            vector = await embedder.embed(text)
        except Exception as exc:
            logger.warning("[backfill] id=%s 임베딩 실패: %s", row_id, exc)
            failed += 1
            continue

        if len(vector) != dim:
            logger.warning(
                "[backfill] id=%s 차원 불일치 (기대 %d, 실제 %d) — 저장하지 않음",
                row_id,
                dim,
                len(vector),
            )
            failed += 1
            continue

        await save(row_id, vector)
        filled += 1

    return BackfillResult(filled=filled, failed=failed)
```

- [ ] **Step 5: 테스트가 통과하는지 확인**

Run: `cd /home/ec2-user/pmhllll12-all/minho && python -m pytest apps/ontology/tests/app/use_cases/test_users_jobs_embedding_backfill.py -v`
Expected: PASS (6 passed)

- [ ] **Step 6: Gemini 어댑터 작성**

`minho/apps/ontology/adapter/outbound/gemini_embedding_client.py`:

```python
"""Gemini 임베딩으로 텍스트를 벡터로 변환한다 (pgvector 저장용).

community 앱에 같은 역할의 클라이언트가 있지만 import-linter contract 2 가
ontology → community 를 금지하므로 여기에 따로 둔다. core.matrix 는 참조 가능하다.
"""

from __future__ import annotations

import asyncio
import logging

from core.matrix.vault_keymaker_secret_manager import keymaker

logger = logging.getLogger(__name__)


class GeminiEmbeddingClient:
    async def embed(self, text: str) -> list[float]:
        vector = await asyncio.to_thread(keymaker.embed_content, text)
        logger.info("[GeminiEmbeddingClient] embed dim=%d", len(vector))
        return vector
```

- [ ] **Step 7: 백필 스크립트 작성**

`minho/apps/ontology/scripts/backfill_users_jobs_embedding.py`:

```python
#!/usr/bin/env python3
"""ontology_users / ontology_jobs 의 embedding 을 Gemini 로 채운다.

embedding IS NULL 인 행만 처리하므로 재실행이 안전하다.

실행 (backend 컨테이너, 작업 디렉터리 /app):
    docker exec pmhllll12-all-backend-1 \
        python apps/ontology/scripts/backfill_users_jobs_embedding.py
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

_ONTOLOGY_ROOT = Path(__file__).resolve().parents[1]
_APPS_ROOT = _ONTOLOGY_ROOT.parent
_MINHO_ROOT = _APPS_ROOT.parent
for _path in (str(_MINHO_ROOT), str(_APPS_ROOT)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("backfill_users_jobs_embedding")

from database import AsyncSessionLocal  # noqa: E402
from ontology.adapter.outbound.gemini_embedding_client import (  # noqa: E402
    GeminiEmbeddingClient,
)
from ontology.app.use_cases.users_jobs_embedding_backfill import (  # noqa: E402
    backfill_rows,
    build_job_text,
    build_user_text,
)
from sqlalchemy import text  # noqa: E402


async def main() -> int:
    if AsyncSessionLocal is None:
        logger.error("DATABASE_URL 이 없어 DB 세션을 만들 수 없습니다.")
        return 1

    embedder = GeminiEmbeddingClient()

    async with AsyncSessionLocal() as session:
        user_rows = (
            await session.execute(
                text(
                    "SELECT id, name, age FROM ontology_users "
                    "WHERE embedding IS NULL ORDER BY id"
                )
            )
        ).all()
        job_rows = (
            await session.execute(
                text(
                    "SELECT id, title, company FROM ontology_jobs "
                    "WHERE embedding IS NULL ORDER BY id"
                )
            )
        ).all()

        async def save_user(row_id: int, vector: list[float]) -> None:
            await session.execute(
                text(
                    "UPDATE ontology_users SET embedding = CAST(:v AS vector) WHERE id = :id"
                ),
                {"v": str(vector), "id": row_id},
            )

        async def save_job(row_id: int, vector: list[float]) -> None:
            await session.execute(
                text(
                    "UPDATE ontology_jobs SET embedding = CAST(:v AS vector) WHERE id = :id"
                ),
                {"v": str(vector), "id": row_id},
            )

        user_result = await backfill_rows(
            [(r.id, build_user_text(r.name, r.age)) for r in user_rows],
            embedder,
            save_user,
        )
        job_result = await backfill_rows(
            [(r.id, build_job_text(r.title, r.company)) for r in job_rows],
            embedder,
            save_job,
        )
        await session.commit()

    logger.info(
        "users filled=%d failed=%d / jobs filled=%d failed=%d",
        user_result.filled,
        user_result.failed,
        job_result.filled,
        job_result.failed,
    )
    return 1 if (user_result.failed or job_result.failed) else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
```

벡터를 `str(vector)`로 넘기는 이유: pgvector는 `'[0.1,0.2,...]'` 형태의 문자열 리터럴을 vector로 캐스팅한다. 파이썬 리스트의 `str()`이 정확히 그 형태다. `CAST(:v AS vector)`를 반드시 붙인다 — 없으면 드라이버가 파라미터를 text 타입으로 보내 `column "embedding" is of type vector but expression is of type text` 오류가 난다.

- [ ] **Step 8: 백필 실행**

```bash
docker exec pmhllll12-all-backend-1 \
  python apps/ontology/scripts/backfill_users_jobs_embedding.py
```

Expected: `users filled=5 failed=0 / jobs filled=5 failed=0`, 종료 코드 0

- [ ] **Step 9: 임베딩이 실제로 채워졌는지 검증**

```bash
docker exec pmhllll12-all-pgvector-1 psql -U postgres -d neondb -c "
select 'users' as t, count(*) filter (where embedding is not null) as filled,
       min(vector_dims(embedding)) as dims from ontology_users
union all
select 'jobs', count(*) filter (where embedding is not null),
       min(vector_dims(embedding)) from ontology_jobs;"
```

Expected: 두 행 모두 `filled=5`, `dims=768`

- [ ] **Step 10: 재실행 멱등성 확인**

```bash
docker exec pmhllll12-all-backend-1 \
  python apps/ontology/scripts/backfill_users_jobs_embedding.py
```

Expected: `users filled=0 failed=0 / jobs filled=0 failed=0` (NULL이 없어 API를 부르지 않는다)

- [ ] **Step 11: 커밋**

```bash
cd /home/ec2-user/pmhllll12-all
git add minho/apps/ontology/app/ports/output/embedding_port.py \
        minho/apps/ontology/adapter/outbound/gemini_embedding_client.py \
        minho/apps/ontology/app/use_cases/users_jobs_embedding_backfill.py \
        minho/apps/ontology/scripts/backfill_users_jobs_embedding.py \
        minho/apps/ontology/tests/app/use_cases/test_users_jobs_embedding_backfill.py
git commit -m "feat: ontology users/jobs 임베딩 백필 추가"
```

---

### Task 4: Neo4j 그래프 동기화

**Files:**
- Modify: `docker-compose.yaml:15-20` (backend `environment:` 블록)
- Create: `minho/apps/ontology/adapter/outbound/neo4j_users_jobs_writer.py`
- Create: `minho/apps/ontology/scripts/sync_users_jobs_to_neo4j.py`
- Test: `minho/apps/ontology/tests/adapter/outbound/test_neo4j_users_jobs_writer.py`

**Interfaces:**
- Consumes: Task 2의 시드 데이터
- Produces: `CONSTRAINT_STATEMENTS: tuple[str, ...]`; `MERGE_USER: str`; `MERGE_JOB: str`; `MERGE_HAS_JOB: str`; `write_graph(session, users: list[dict], jobs: list[dict]) -> None`

- [ ] **Step 1: compose 에 NEO4J 환경변수 추가**

`docker-compose.yaml`의 backend `environment:` 블록(현재 15~20행) 마지막에 세 줄을 더한다:

```yaml
      NEO4J_URI: bolt://neo4j:7687
      NEO4J_USER: neo4j
      NEO4J_PASSWORD: ${NEO4J_PASSWORD}
```

- [ ] **Step 2: backend 재생성 후 주입 확인**

```bash
cd /home/ec2-user/pmhllll12-all
docker compose up -d backend
docker exec pmhllll12-all-backend-1 sh -lc 'env | grep -c "^NEO4J_"'
```

Expected: `3`

- [ ] **Step 3: 실패하는 테스트 작성**

`minho/apps/ontology/tests/adapter/outbound/test_neo4j_users_jobs_writer.py`:

```python
from __future__ import annotations

from ontology.adapter.outbound.neo4j_users_jobs_writer import (
    CONSTRAINT_STATEMENTS,
    MERGE_HAS_JOB,
    MERGE_JOB,
    MERGE_USER,
    write_graph,
)


class _FakeSession:
    def __init__(self):
        self.runs: list[tuple[str, dict]] = []

    def run(self, query, **params):
        self.runs.append((query, params))


def test_constraints_cover_user_and_job():
    joined = " ".join(CONSTRAINT_STATEMENTS)
    assert "u:User" in joined
    assert "j:Job" in joined
    assert joined.count("IF NOT EXISTS") == 2


def test_merge_statements_use_merge_not_create():
    for query in (MERGE_USER, MERGE_JOB, MERGE_HAS_JOB):
        assert "MERGE" in query
        assert "CREATE (" not in query


def test_write_graph_runs_constraints_then_nodes_then_relationships():
    session = _FakeSession()
    users = [{"id": 1, "name": "김민준", "email": "minjun.kim@example.com", "age": 32}]
    jobs = [{"id": 1, "title": "백엔드 개발자", "company": "카카오", "userid": 1}]

    write_graph(session, users, jobs)

    queries = [q for q, _ in session.runs]
    assert len(queries) == 2 + 1 + 1 + 1  # 제약 2 + user 1 + job 1 + 관계 1
    assert queries[0] in CONSTRAINT_STATEMENTS
    assert queries[1] in CONSTRAINT_STATEMENTS
    assert queries[2] == MERGE_USER
    assert queries[3] == MERGE_JOB
    assert queries[4] == MERGE_HAS_JOB


def test_write_graph_passes_row_values_as_parameters():
    session = _FakeSession()
    users = [{"id": 7, "name": "정하은", "email": "haeun.jung@example.com", "age": 35}]
    jobs = [{"id": 9, "title": "머신러닝 엔지니어", "company": "라인", "userid": 7}]

    write_graph(session, users, jobs)

    _, user_params = session.runs[2]
    assert user_params == {
        "id": 7,
        "name": "정하은",
        "email": "haeun.jung@example.com",
        "age": 35,
    }
    _, rel_params = session.runs[4]
    assert rel_params == {"userid": 7, "jobid": 9}
```

- [ ] **Step 4: 테스트가 실패하는지 확인**

Run: `cd /home/ec2-user/pmhllll12-all/minho && python -m pytest apps/ontology/tests/adapter/outbound/test_neo4j_users_jobs_writer.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'ontology.adapter.outbound.neo4j_users_jobs_writer'`

- [ ] **Step 5: Cypher 작성기 구현**

`minho/apps/ontology/adapter/outbound/neo4j_users_jobs_writer.py`:

```python
"""ontology_users / ontology_jobs 를 Neo4j 그래프로 적재한다.

(:User)-[:HAS_JOB]->(:Job) 이고 company 는 Job 의 속성이다.
드라이버 세션을 주입받아 테스트 시 가짜 세션을 넣을 수 있게 한다.
"""

from __future__ import annotations

from collections.abc import Sequence

CONSTRAINT_STATEMENTS: tuple[str, ...] = (
    "CREATE CONSTRAINT user_id_unique IF NOT EXISTS "
    "FOR (u:User) REQUIRE u.id IS UNIQUE",
    "CREATE CONSTRAINT job_id_unique IF NOT EXISTS "
    "FOR (j:Job) REQUIRE j.id IS UNIQUE",
)

MERGE_USER = (
    "MERGE (u:User {id: $id}) "
    "SET u.name = $name, u.email = $email, u.age = $age"
)

MERGE_JOB = (
    "MERGE (j:Job {id: $id}) "
    "SET j.title = $title, j.company = $company"
)

MERGE_HAS_JOB = (
    "MATCH (u:User {id: $userid}), (j:Job {id: $jobid}) "
    "MERGE (u)-[:HAS_JOB]->(j)"
)


def write_graph(
    session,
    users: Sequence[dict],
    jobs: Sequence[dict],
) -> None:
    """제약 → 노드 → 관계 순으로 적재한다. MERGE 라 재실행해도 중복되지 않는다."""
    for statement in CONSTRAINT_STATEMENTS:
        session.run(statement)

    for user in users:
        session.run(
            MERGE_USER,
            id=user["id"],
            name=user["name"],
            email=user["email"],
            age=user["age"],
        )

    for job in jobs:
        session.run(
            MERGE_JOB,
            id=job["id"],
            title=job["title"],
            company=job["company"],
        )

    for job in jobs:
        session.run(MERGE_HAS_JOB, userid=job["userid"], jobid=job["id"])
```

- [ ] **Step 6: 테스트가 통과하는지 확인**

Run: `cd /home/ec2-user/pmhllll12-all/minho && python -m pytest apps/ontology/tests/adapter/outbound/test_neo4j_users_jobs_writer.py -v`
Expected: PASS (4 passed)

- [ ] **Step 7: 동기화 스크립트 작성**

`minho/apps/ontology/scripts/sync_users_jobs_to_neo4j.py`:

```python
#!/usr/bin/env python3
"""Postgres 의 ontology_users / ontology_jobs 를 Neo4j 그래프로 동기화한다.

Postgres 가 정본이고 Neo4j 는 파생이다. 단방향이며 MERGE 라 재실행이 안전하다.

실행 (backend 컨테이너, 작업 디렉터리 /app):
    docker exec pmhllll12-all-backend-1 \
        python apps/ontology/scripts/sync_users_jobs_to_neo4j.py
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from pathlib import Path

_ONTOLOGY_ROOT = Path(__file__).resolve().parents[1]
_APPS_ROOT = _ONTOLOGY_ROOT.parent
_MINHO_ROOT = _APPS_ROOT.parent
for _path in (str(_MINHO_ROOT), str(_APPS_ROOT)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("sync_users_jobs_to_neo4j")

from database import AsyncSessionLocal  # noqa: E402
from neo4j import GraphDatabase  # noqa: E402
from ontology.adapter.outbound.neo4j_users_jobs_writer import write_graph  # noqa: E402
from sqlalchemy import text  # noqa: E402


async def _load_rows() -> tuple[list[dict], list[dict]]:
    async with AsyncSessionLocal() as session:
        users = (
            await session.execute(
                text("SELECT id, name, email, age FROM ontology_users ORDER BY id")
            )
        ).mappings().all()
        jobs = (
            await session.execute(
                text("SELECT id, title, company, userid FROM ontology_jobs ORDER BY id")
            )
        ).mappings().all()
    return [dict(r) for r in users], [dict(r) for r in jobs]


def main() -> int:
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    if not (uri and user and password):
        logger.error("NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD 가 필요합니다.")
        return 1

    if AsyncSessionLocal is None:
        logger.error("DATABASE_URL 이 없어 DB 세션을 만들 수 없습니다.")
        return 1

    users, jobs = asyncio.run(_load_rows())
    logger.info("Postgres 에서 users=%d jobs=%d 읽음", len(users), len(jobs))

    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        driver.verify_connectivity()
        with driver.session() as session:
            write_graph(session, users, jobs)
            counts = session.run(
                "MATCH (u:User) WITH count(u) AS users "
                "MATCH (j:Job) WITH users, count(j) AS jobs "
                "MATCH ()-[r:HAS_JOB]->() "
                "RETURN users, jobs, count(r) AS rels"
            ).single()
        logger.info(
            "Neo4j 적재 완료 — User=%d Job=%d HAS_JOB=%d",
            counts["users"],
            counts["jobs"],
            counts["rels"],
        )
    finally:
        driver.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 8: 동기화 실행**

```bash
docker exec pmhllll12-all-backend-1 \
  python apps/ontology/scripts/sync_users_jobs_to_neo4j.py
```

Expected: `Postgres 에서 users=5 jobs=5 읽음`, `Neo4j 적재 완료 — User=5 Job=5 HAS_JOB=5`

- [ ] **Step 9: 그래프 직접 검증**

```bash
NEO4J_PW=$(grep -m1 '^NEO4J_PASSWORD=' /home/ec2-user/pmhllll12-all/.env | cut -d= -f2-)
docker exec -e PW="$NEO4J_PW" pmhllll12-all-backend-1 python -c "
import os
from neo4j import GraphDatabase
d = GraphDatabase.driver('bolt://neo4j:7687', auth=('neo4j', os.environ['PW']))
with d.session() as s:
    for r in s.run('MATCH (u:User)-[:HAS_JOB]->(j:Job) RETURN u.name AS name, j.title AS title, j.company AS company ORDER BY u.id'):
        print(r['name'], '|', r['title'], '|', r['company'])
d.close()
"
```

Expected: 5행. `김민준 | 백엔드 개발자 | 카카오` … `정하은 | 머신러닝 엔지니어 | 라인`

- [ ] **Step 10: 멱등성 확인 — 두 번 더 실행**

```bash
docker exec pmhllll12-all-backend-1 \
  python apps/ontology/scripts/sync_users_jobs_to_neo4j.py
docker exec pmhllll12-all-backend-1 \
  python apps/ontology/scripts/sync_users_jobs_to_neo4j.py
```

Expected: 매번 `User=5 Job=5 HAS_JOB=5` — 숫자가 늘지 않는다.

- [ ] **Step 11: 커밋**

```bash
cd /home/ec2-user/pmhllll12-all
git add docker-compose.yaml \
        minho/apps/ontology/adapter/outbound/neo4j_users_jobs_writer.py \
        minho/apps/ontology/scripts/sync_users_jobs_to_neo4j.py \
        minho/apps/ontology/tests/adapter/outbound/test_neo4j_users_jobs_writer.py
git commit -m "feat: ontology users/jobs Neo4j 그래프 동기화 추가"
```

---

### Task 5: 전체 회귀 검증

**Files:**
- Modify: 없음 (검증만 한다. 실패가 나오면 해당 Task로 돌아간다)

**Interfaces:**
- Consumes: Task 1~4의 모든 산출물
- Produces: 없음

- [ ] **Step 1: 전체 테스트 실행**

Run: `cd /home/ec2-user/pmhllll12-all/minho && python -m pytest -q`
Expected: 기존 테스트가 모두 통과하고, 이번에 추가한 18개(ORM 4 + 시드 4 + 백필 6 + Neo4j 작성기 4)가 함께 통과한다. 실패가 있으면 이 계획 이전에도 실패했는지 `git stash`로 확인한다.

- [ ] **Step 2: import 경계 검증**

Run: `cd /home/ec2-user/pmhllll12-all/minho && lint-imports`
Expected: 모든 contract가 KEPT. 특히 contract 2(`온톨로지·공통 인프라는 허브/스포크를 모른다`)가 깨지지 않아야 한다 — `ontology`가 `community`를 import하면 여기서 잡힌다.

- [ ] **Step 3: 린트·포맷 검증**

```bash
cd /home/ec2-user/pmhllll12-all/minho
ruff check apps/ontology alembic/versions/20260730_0002_create_ontology_users_jobs.py alembic/versions/20260730_0003_seed_ontology_users_jobs.py
ruff format --check apps/ontology
```

Expected: 위반 없음. 스크립트의 `# noqa: E402`가 있어 sys.path 조작 후 import는 통과한다.

- [ ] **Step 4: 최종 상태 요약 검증**

```bash
docker exec pmhllll12-all-backend-1 alembic current
docker exec pmhllll12-all-pgvector-1 psql -U postgres -d neondb -tAc "
select 'users=' || (select count(*) from ontology_users)
    || ' jobs=' || (select count(*) from ontology_jobs)
    || ' embedded=' || (select count(*) from ontology_users where embedding is not null)
                     + (select count(*) from ontology_jobs where embedding is not null);"
```

Expected: `20260730_0003 (head)` 그리고 `users=5 jobs=5 embedded=10`

- [ ] **Step 5: 커밋 (변경이 있을 때만)**

Step 1~3에서 고친 게 있으면 커밋한다. 없으면 건너뛴다.

```bash
cd /home/ec2-user/pmhllll12-all
git status --short
```

---

## 롤백 방법

문제가 생기면 아래 순서로 되돌린다.

```bash
# 1. Neo4j 그래프 제거
docker exec pmhllll12-all-backend-1 python -c "
import os
from neo4j import GraphDatabase
d = GraphDatabase.driver(os.environ['NEO4J_URI'], auth=(os.environ['NEO4J_USER'], os.environ['NEO4J_PASSWORD']))
with d.session() as s:
    s.run('MATCH (n) WHERE n:User OR n:Job DETACH DELETE n')
    s.run('DROP CONSTRAINT user_id_unique IF EXISTS')
    s.run('DROP CONSTRAINT job_id_unique IF EXISTS')
d.close()
"

# 2. Postgres 테이블 제거
docker exec pmhllll12-all-backend-1 alembic downgrade 20260730_0001
```

`DETACH DELETE`를 `n:User OR n:Job`으로 한정한 이유는 그래프에 다른 데이터가 생겼을 때 함께 지우지 않기 위해서다.
