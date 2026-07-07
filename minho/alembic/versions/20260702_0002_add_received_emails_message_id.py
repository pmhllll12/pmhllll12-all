"""community_received_emails 에 message_id 컬럼(중복 방지용 UNIQUE) 추가.

Revision ID: 20260702_0002
Revises: 20260702_0001
Create Date: 2026-07-02
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260702_0002"
down_revision = "20260702_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    columns = {col["name"] for col in inspect(bind).get_columns("community_received_emails")}

    if "message_id" not in columns:
        op.add_column(
            "community_received_emails",
            sa.Column("message_id", sa.String(length=255), nullable=True),
        )
        op.create_unique_constraint(
            "uq_community_received_emails_message_id",
            "community_received_emails",
            ["message_id"],
        )


def downgrade() -> None:
    bind = op.get_bind()
    columns = {col["name"] for col in inspect(bind).get_columns("community_received_emails")}

    if "message_id" in columns:
        op.drop_constraint(
            "uq_community_received_emails_message_id",
            "community_received_emails",
            type_="unique",
        )
        op.drop_column("community_received_emails", "message_id")
