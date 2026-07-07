"""community_received_emails 테이블 생성 (pgvector 임베딩 컬럼 포함).

Revision ID: 20260702_0001
Revises: 20260617_0001
Create Date: 2026-07-02
"""

from __future__ import annotations

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy import inspect

from alembic import op

revision = "20260702_0001"
down_revision = "20260617_0001"
branch_labels = None
depends_on = None

_EMBEDDING_DIM = 768


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())

    if "community_received_emails" not in tables:
        op.create_table(
            "community_received_emails",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, primary_key=True),
            sa.Column("subject", sa.String(length=500), nullable=False, server_default=""),
            sa.Column("from_email", sa.String(length=320), nullable=False, server_default=""),
            sa.Column("to_email", sa.String(length=320), nullable=False, server_default=""),
            sa.Column("body", sa.Text(), nullable=False, server_default=""),
            sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("embedding", Vector(_EMBEDDING_DIM), nullable=False),
        )
        op.create_index(
            "ix_community_received_emails_from_email",
            "community_received_emails",
            ["from_email"],
        )


def downgrade() -> None:
    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())

    if "community_received_emails" in tables:
        op.drop_table("community_received_emails")
