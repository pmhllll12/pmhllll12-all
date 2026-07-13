"""moneyball 축구 ERD 테이블 생성 (stadium/team/schedule/player, pgvector 확장 포함).

Revision ID: 20260713_0001
Revises: 20260703_0002
Create Date: 2026-07-13
"""

from __future__ import annotations

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy import inspect

from alembic import op

revision = "20260713_0001"
down_revision = "20260703_0002"
branch_labels = None
depends_on = None

_EMBEDDING_DIM = 768


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())

    if "moneyball_stadiums" not in tables:
        op.create_table(
            "moneyball_stadiums",
            sa.Column("stadium_id", sa.String(length=10), nullable=False, primary_key=True),
            # ERD 원본 오탈자(statdium_name)를 그대로 유지
            sa.Column("statdium_name", sa.String(length=40), nullable=True),
            sa.Column("hometeam_id", sa.String(length=10), nullable=True),
            sa.Column("seat_count", sa.Integer(), nullable=True),
            sa.Column("address", sa.String(length=60), nullable=True),
            sa.Column("ddd", sa.String(length=10), nullable=True),
            sa.Column("tel", sa.String(length=10), nullable=True),
        )

    if "moneyball_teams" not in tables:
        op.create_table(
            "moneyball_teams",
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
                sa.ForeignKey("moneyball_stadiums.stadium_id"),
                nullable=True,
            ),
        )

    if "moneyball_schedules" not in tables:
        op.create_table(
            "moneyball_schedules",
            # ERD상 sche_date + stadium_id 복합 기본키
            sa.Column("sche_date", sa.String(length=10), nullable=False, primary_key=True),
            sa.Column(
                "stadium_id",
                sa.String(length=10),
                sa.ForeignKey("moneyball_stadiums.stadium_id"),
                nullable=False,
                primary_key=True,
            ),
            sa.Column("gubun", sa.String(length=10), nullable=True),
            sa.Column("hometeam_id", sa.String(length=10), nullable=True),
            sa.Column("awayteam_id", sa.String(length=10), nullable=True),
            sa.Column("home_score", sa.Integer(), nullable=True),
            sa.Column("away_score", sa.Integer(), nullable=True),
        )

    if "moneyball_players" not in tables:
        op.create_table(
            "moneyball_players",
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
                "team_id",
                sa.String(length=10),
                sa.ForeignKey("moneyball_teams.team_id"),
                nullable=True,
            ),
            # 향후 선수 유사도 검색용 — 지금은 채우는 파이프라인 없이 구조만 준비
            sa.Column("embedding", Vector(_EMBEDDING_DIM), nullable=True),
        )


def downgrade() -> None:
    bind = op.get_bind()
    tables = set(inspect(bind).get_table_names())

    if "moneyball_players" in tables:
        op.drop_table("moneyball_players")
    if "moneyball_schedules" in tables:
        op.drop_table("moneyball_schedules")
    if "moneyball_teams" in tables:
        op.drop_table("moneyball_teams")
    if "moneyball_stadiums" in tables:
        op.drop_table("moneyball_stadiums")
