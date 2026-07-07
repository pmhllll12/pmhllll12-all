"""Titanic Person / Booking 테이블 (Neon).

Revision ID: 20260204_0001
Revises:
Create Date: 2026-02-04
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "20260204_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "titanic_persons",
        sa.Column("passenger_id", sa.String(length=64), nullable=False),
        sa.Column("booking_id", sa.String(length=64), nullable=False),
        sa.Column("embarked_code", sa.String(length=8), nullable=False, server_default=""),
        sa.Column("name", sa.String(length=512), nullable=False),
        sa.Column("gender", sa.String(length=32), nullable=False),
        sa.Column("age", sa.String(length=32), nullable=False, server_default=""),
        sa.Column("sib_sp", sa.String(length=16), nullable=False, server_default="0"),
        sa.Column("parch", sa.String(length=16), nullable=False, server_default="0"),
        sa.Column("survived", sa.String(length=8), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("passenger_id"),
    )
    op.create_index(
        "ix_titanic_persons_booking_id",
        "titanic_persons",
        ["booking_id"],
        unique=False,
    )

    op.create_table(
        "titanic_bookings",
        sa.Column("booking_id", sa.String(length=64), nullable=False),
        sa.Column("pclass", sa.String(length=8), nullable=False),
        sa.Column("ticket", sa.String(length=128), nullable=False, server_default=""),
        sa.Column("fare", sa.String(length=32), nullable=False, server_default="0"),
        sa.Column("cabin", sa.String(length=64), nullable=False, server_default=""),
        sa.Column("embarked_code", sa.String(length=8), nullable=False, server_default=""),
        sa.Column("port_name", sa.String(length=128), nullable=False, server_default=""),
        sa.PrimaryKeyConstraint("booking_id"),
    )


def downgrade() -> None:
    op.drop_table("titanic_bookings")
    op.drop_table("titanic_persons")
