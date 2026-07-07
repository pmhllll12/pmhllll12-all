"""vision_analyzed_images 에 image_key 컬럼 추가 (S3 저장 객체 키).

Revision ID: 20260703_0002
Revises: 20260703_0001
Create Date: 2026-07-03
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260703_0002"
down_revision = "20260703_0001"
branch_labels = None
depends_on = None

_TABLE = "vision_analyzed_images"
_COLUMN = "image_key"


def upgrade() -> None:
    bind = op.get_bind()
    columns = {col["name"] for col in inspect(bind).get_columns(_TABLE)}

    if _COLUMN not in columns:
        op.add_column(
            _TABLE,
            sa.Column(_COLUMN, sa.String(length=1024), nullable=False, server_default=""),
        )


def downgrade() -> None:
    bind = op.get_bind()
    columns = {col["name"] for col in inspect(bind).get_columns(_TABLE)}

    if _COLUMN in columns:
        op.drop_column(_TABLE, _COLUMN)
