"""vision_analyzed_images 테이블 생성 (이미지 캡션·태그 저장).

Revision ID: 20260703_0001
Revises: 20260702_0002
Create Date: 2026-07-03
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260703_0001"
down_revision = "20260702_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())

    if "vision_analyzed_images" not in tables:
        op.create_table(
            "vision_analyzed_images",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, primary_key=True),
            sa.Column("filename", sa.String(length=500), nullable=False, server_default=""),
            sa.Column("caption", sa.Text(), nullable=False, server_default=""),
            sa.Column("tags", sa.ARRAY(sa.String(length=100)), nullable=False, server_default="{}"),
            sa.Column("analyzed_at", sa.DateTime(timezone=True), nullable=False),
        )


def downgrade() -> None:
    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())

    if "vision_analyzed_images" in tables:
        op.drop_table("vision_analyzed_images")
