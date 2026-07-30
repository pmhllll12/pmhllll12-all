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
