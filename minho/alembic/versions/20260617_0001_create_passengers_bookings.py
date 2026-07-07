"""passengers / bookings 테이블 생성 (JackTrainerOrm / RoseModelOrm).

Revision ID: 20260617_0001
Revises: 20260522_0001
Create Date: 2026-06-17
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260617_0001"
down_revision = "20260522_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())

    if "passengers" not in tables:
        op.create_table(
            "passengers",
            sa.Column("passenger_id", sa.String(), nullable=True, primary_key=True),
            sa.Column("name",         sa.String(), nullable=True),
            sa.Column("gender",       sa.String(), nullable=True),
            sa.Column("age",          sa.String(), nullable=True),
            sa.Column("sib_sp",       sa.String(), nullable=True),
            sa.Column("parch",        sa.String(), nullable=True),
            sa.Column("survived",     sa.String(), nullable=True),
        )

    if "bookings" not in tables:
        op.create_table(
            "bookings",
            sa.Column("id",          sa.Integer(), autoincrement=True, nullable=False, primary_key=True),
            sa.Column("passenger_id", sa.String(),  sa.ForeignKey("passengers.passenger_id"), nullable=True),
            sa.Column("pclass",      sa.String(), nullable=True),
            sa.Column("ticket",      sa.String(), nullable=True),
            sa.Column("fare",        sa.String(), nullable=True),
            sa.Column("cabin",       sa.String(), nullable=True),
            sa.Column("embarked",    sa.String(), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())

    if "bookings" in tables:
        op.drop_table("bookings")
    if "passengers" in tables:
        op.drop_table("passengers")
