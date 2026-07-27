"""admin_pdf_summaries 테이블 생성 (PDF 업로드 추출·요약 결과 저장).

Revision ID: 20260727_0001
Revises: 20260713_0002
Create Date: 2026-07-27
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260727_0001"
down_revision = "20260713_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())

    if "admin_pdf_summaries" not in tables:
        op.create_table(
            "admin_pdf_summaries",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False, primary_key=True),
            sa.Column("filename", sa.String(length=500), nullable=False, server_default=""),
            sa.Column("char_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("summary", sa.Text(), nullable=False, server_default=""),
            sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        )


def downgrade() -> None:
    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())

    if "admin_pdf_summaries" in tables:
        op.drop_table("admin_pdf_summaries")
