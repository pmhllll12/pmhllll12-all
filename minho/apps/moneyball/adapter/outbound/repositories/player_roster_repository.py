from __future__ import annotations

from moneyball.adapter.outbound.mappers.player_mapper import player_entity_from_orm
from moneyball.adapter.outbound.orm.player_orm import PlayerOrm
from moneyball.app.ports.output.player_roster_port import PlayerRosterPort
from moneyball.domain.entities.player_entity import PlayerEntity
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class PlayerRosterRepository(PlayerRosterPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_players_by_team(self, team_id: str) -> list[PlayerEntity]:
        stmt = select(PlayerOrm).where(PlayerOrm.team_id == team_id)
        result = await self.session.execute(stmt)
        return [player_entity_from_orm(orm) for orm in result.scalars().all()]


__all__ = ["PlayerRosterRepository"]
