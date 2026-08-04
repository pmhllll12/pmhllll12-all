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
