"""기존 `titanic_james_*` 테이블을 `titanic_*` 로 이름만 변경 (데이터 유지).

Revision ID: 20260520_0002
Revises: 20260204_0001
Create Date: 2026-05-20
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260520_0002"
down_revision = "20260204_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())

    def _count(tbl: str) -> int:
        return int(bind.execute(sa.text(f'SELECT COUNT(*) FROM "{tbl}"')).scalar() or 0)

    if "titanic_james_bookings" in tables:
        if "titanic_bookings" in tables:
            if _count("titanic_bookings") > 0:
                raise RuntimeError(
                    "`titanic_bookings` 와 `titanic_james_bookings` 가 동시에 있고 "
                    "`titanic_bookings` 에 행이 있어 자동 이름 변경을 건너뜁니다. "
                    "데이터를 정리한 뒤 다시 마이그레이션하세요."
                )
            op.drop_table("titanic_bookings")
        op.rename_table("titanic_james_bookings", "titanic_bookings")

    if "titanic_james_persons" in tables:
        if "titanic_persons" in tables:
            if _count("titanic_persons") > 0:
                raise RuntimeError(
                    "`titanic_persons` 와 `titanic_james_persons` 가 동시에 있고 "
                    "`titanic_persons` 에 행이 있어 자동 이름 변경을 건너뜁니다. "
                    "데이터를 정리한 뒤 다시 마이그레이션하세요."
                )
            op.drop_table("titanic_persons")
        op.rename_table("titanic_james_persons", "titanic_persons")
        insp = inspect(bind)
        idx_names = {ix["name"] for ix in insp.get_indexes("titanic_persons")}
        if "ix_titanic_james_persons_booking_id" in idx_names:
            op.execute(
                sa.text(
                    "ALTER INDEX ix_titanic_james_persons_booking_id "
                    "RENAME TO ix_titanic_persons_booking_id"
                )
            )


def downgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)
    tables = set(insp.get_table_names())

    if "titanic_bookings" in tables and "titanic_james_bookings" not in tables:
        op.rename_table("titanic_bookings", "titanic_james_bookings")

    if "titanic_persons" in tables and "titanic_james_persons" not in tables:
        idx_names = {ix["name"] for ix in insp.get_indexes("titanic_persons")}
        if "ix_titanic_persons_booking_id" in idx_names:
            op.execute(
                sa.text(
                    "ALTER INDEX ix_titanic_persons_booking_id "
                    "RENAME TO ix_titanic_james_persons_booking_id"
                )
            )
        op.rename_table("titanic_persons", "titanic_james_persons")
