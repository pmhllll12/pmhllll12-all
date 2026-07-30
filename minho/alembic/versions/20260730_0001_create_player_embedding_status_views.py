"""선수 임베딩 진행 상황 확인용 뷰 2개 생성 (pgAdmin 에서 바로 보기 위함).

Revision ID: 20260730_0001
Revises: 20260727_0001
Create Date: 2026-07-30
"""

from __future__ import annotations

from alembic import op

revision = "20260730_0001"
down_revision = "20260727_0001"
branch_labels = None
depends_on = None

# 선수별 상태. UPDATE 된 행은 힙 끝으로 밀려 정렬 없이 보면 찾기 어려우므로
# 뷰에서 미완료 → 완료 순, 그 다음 player_id 순으로 고정해 둔다.
_STATUS_VIEW = """
CREATE OR REPLACE VIEW moneyball_player_embedding_status AS
SELECT
    p.player_id,
    p.player_name,
    p.position,
    t.team_name,
    CASE WHEN p.embedding IS NULL THEN '❌ 미완료' ELSE '✅ 완료' END AS embedding_status,
    CASE WHEN p.embedding IS NULL THEN NULL ELSE vector_dims(p.embedding) END AS embedding_dims
FROM moneyball_players p
LEFT JOIN moneyball_teams t ON p.team_id = t.team_id
ORDER BY (p.embedding IS NOT NULL), p.player_id
"""

# 한 줄 요약 — 이 행만 보면 전체가 끝났는지 알 수 있다.
_SUMMARY_VIEW = """
CREATE OR REPLACE VIEW moneyball_player_embedding_summary AS
SELECT
    count(*) AS total_players,
    count(embedding) AS embedded,
    count(*) - count(embedding) AS missing,
    round(100.0 * count(embedding) / NULLIF(count(*), 0), 1) AS progress_pct,
    CASE
        WHEN count(*) = 0 THEN '⚠️ 선수 데이터 없음'
        WHEN count(embedding) = count(*) THEN '✅ 임베딩 완료 — 전체 선수 채워짐'
        WHEN count(embedding) = 0 THEN '❌ 임베딩 없음 — 백필 스크립트 실행 필요'
        ELSE '⏳ 진행 중 — 백필 스크립트를 다시 실행하면 이어서 채운다'
    END AS status_message
FROM moneyball_players
"""


def upgrade() -> None:
    op.execute(_STATUS_VIEW)
    op.execute(_SUMMARY_VIEW)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS moneyball_player_embedding_summary")
    op.execute("DROP VIEW IF EXISTS moneyball_player_embedding_status")
