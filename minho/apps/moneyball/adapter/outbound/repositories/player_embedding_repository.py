"""`moneyball_players.embedding` 읽기·쓰기 (pgvector)."""

from __future__ import annotations

import logging

from moneyball.adapter.outbound.mappers.player_mapper import player_profile_from_orm

# 네 ORM 은 문자열 relationship 으로 서로를 참조한다 — 일부만 임포트하면 매퍼 설정이
# 'StadiumOrm' 을 찾지 못해 첫 쿼리에서 InvalidRequestError 가 난다. 앱 기동 경로에서는
# database.create_all_tables() 가 넷을 모두 임포트하지만 CLI 는 그렇지 않다.
from moneyball.adapter.outbound.orm import schedule_orm, stadium_orm  # noqa: F401
from moneyball.adapter.outbound.orm.player_orm import PlayerOrm
from moneyball.adapter.outbound.orm.team_orm import TeamOrm
from moneyball.app.dtos.player_embedding_dto import PlayerProfile
from moneyball.app.ports.output.player_embedding_port import PlayerEmbeddingPort
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class PlayerEmbeddingRepository(PlayerEmbeddingPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def count_missing(self) -> int:
        """백필 대상 건수 — 실행 전후 확인용."""
        stmt = select(func.count()).select_from(PlayerOrm).where(PlayerOrm.embedding.is_(None))
        return int((await self.session.execute(stmt)).scalar_one())

    async def list_targets(
        self, limit: int, overwrite: bool, after_player_id: str | None = None
    ) -> list[PlayerProfile]:
        stmt = (
            select(PlayerOrm, TeamOrm.team_name)
            .outerjoin(TeamOrm, PlayerOrm.team_id == TeamOrm.team_id)
            .order_by(PlayerOrm.player_id)
            .limit(limit)
        )
        if not overwrite:
            stmt = stmt.where(PlayerOrm.embedding.is_(None))
        if after_player_id is not None:
            stmt = stmt.where(PlayerOrm.player_id > after_player_id)

        rows = (await self.session.execute(stmt)).all()
        return [player_profile_from_orm(orm, team_name) for orm, team_name in rows]

    async def save_embedding(self, player_id: str, embedding: list[float]) -> None:
        await self.session.execute(
            update(PlayerOrm).where(PlayerOrm.player_id == player_id).values(embedding=embedding)
        )

    async def commit(self) -> None:
        await self.session.commit()


__all__ = ["PlayerEmbeddingRepository"]
