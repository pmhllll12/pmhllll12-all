"""stadium / team / schedule / player 테이블 생성 (moneyball 축구 데이터셋).

Revision ID: 20260713_0001
Revises: 20260703_0002
Create Date: 2026-07-13
"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260713_0001"
down_revision = "20260703_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())

    if "stadium" not in tables:
        op.create_table(
            "stadium",
            sa.Column("stadium_id", sa.String(length=10), nullable=False, primary_key=True),
            sa.Column("stadium_name", sa.String(length=40), nullable=True),
            sa.Column("hometeam_id", sa.String(length=10), nullable=True),
            sa.Column("seat_count", sa.Integer(), nullable=True),
            sa.Column("address", sa.String(length=60), nullable=True),
            sa.Column("ddd", sa.String(length=10), nullable=True),
            sa.Column("tel", sa.String(length=10), nullable=True),
        )

    if "team" not in tables:
        op.create_table(
            "team",
            sa.Column("team_id", sa.String(length=10), nullable=False, primary_key=True),
            sa.Column("region_name", sa.String(length=10), nullable=True),
            sa.Column("team_name", sa.String(length=40), nullable=True),
            sa.Column("e_team_name", sa.String(length=50), nullable=True),
            sa.Column("orig_yyyy", sa.String(length=10), nullable=True),
            sa.Column("zip_code1", sa.String(length=10), nullable=True),
            sa.Column("zip_code2", sa.String(length=10), nullable=True),
            sa.Column("address", sa.String(length=80), nullable=True),
            sa.Column("ddd", sa.String(length=10), nullable=True),
            sa.Column("tel", sa.String(length=10), nullable=True),
            sa.Column("fax", sa.String(length=10), nullable=True),
            sa.Column("homepage", sa.String(length=50), nullable=True),
            sa.Column("owner", sa.String(length=10), nullable=True),
            sa.Column(
                "stadium_id",
                sa.String(length=10),
                sa.ForeignKey("stadium.stadium_id"),
                nullable=True,
            ),
        )

    if "schedule" not in tables:
        op.create_table(
            "schedule",
            sa.Column("sche_date", sa.String(length=10), nullable=False, primary_key=True),
            sa.Column(
                "stadium_id",
                sa.String(length=10),
                sa.ForeignKey("stadium.stadium_id"),
                nullable=False,
                primary_key=True,
            ),
            sa.Column("gubun", sa.String(length=10), nullable=True),
            sa.Column(
                "hometeam_id", sa.String(length=10), sa.ForeignKey("team.team_id"), nullable=True
            ),
            sa.Column(
                "awayteam_id", sa.String(length=10), sa.ForeignKey("team.team_id"), nullable=True
            ),
            sa.Column("home_score", sa.Integer(), nullable=True),
            sa.Column("away_score", sa.Integer(), nullable=True),
        )

    if "player" not in tables:
        op.create_table(
            "player",
            sa.Column("player_id", sa.String(length=10), nullable=False, primary_key=True),
            sa.Column("player_name", sa.String(length=20), nullable=True),
            sa.Column("e_player_name", sa.String(length=40), nullable=True),
            sa.Column("nickname", sa.String(length=30), nullable=True),
            sa.Column("join_yyyy", sa.String(length=10), nullable=True),
            sa.Column("position", sa.String(length=10), nullable=True),
            sa.Column("back_no", sa.Integer(), nullable=True),
            sa.Column("nation", sa.String(length=20), nullable=True),
            sa.Column("birth_date", sa.Date(), nullable=True),
            sa.Column("solar", sa.String(length=10), nullable=True),
            sa.Column("height", sa.Integer(), nullable=True),
            sa.Column("weight", sa.Integer(), nullable=True),
            sa.Column(
                "team_id", sa.String(length=10), sa.ForeignKey("team.team_id"), nullable=True
            ),
        )


def downgrade() -> None:
    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())

    if "player" in tables:
        op.drop_table("player")
    if "schedule" in tables:
        op.drop_table("schedule")
    if "team" in tables:
        op.drop_table("team")
    if "stadium" in tables:
        op.drop_table("stadium")
