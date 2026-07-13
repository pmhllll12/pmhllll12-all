"""stadium / team / schedule / player 시드 데이터 적재 (moneyball 축구 데이터셋).

`apps/moneyball/resources/soccer_seed_data.sql`의 INSERT 문을 그대로 실행한다.
이미 데이터가 있으면(재실행·다운그레이드 후 재적용 등) 건너뛴다.

Revision ID: 20260713_0002
Revises: 20260713_0001
Create Date: 2026-07-13
"""

from __future__ import annotations

from pathlib import Path

import sqlalchemy as sa

from alembic import op

revision = "20260713_0002"
down_revision = "20260713_0001"
branch_labels = None
depends_on = None

_MONEYBALL_APP_ROOT = Path(__file__).resolve().parents[2] / "apps" / "moneyball"
_SEED_FILE = _MONEYBALL_APP_ROOT / "resources" / "soccer_seed_data.sql"


def upgrade() -> None:
    bind = op.get_bind()
    already_seeded = bind.execute(sa.text("SELECT count(*) FROM stadium")).scalar_one()
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
    for table in ("schedule", "player", "team", "stadium"):
        bind.execute(sa.text(f"DELETE FROM {table}"))
