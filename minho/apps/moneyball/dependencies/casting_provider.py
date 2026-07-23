from __future__ import annotations

from fastapi import Depends
from moneyball.adapter.outbound.repositories.player_roster_repository import (
    PlayerRosterRepository,
)
from moneyball.app.ports.input.casting_use_case import CastingUseCase
from moneyball.app.ports.output.player_roster_port import PlayerRosterPort
from moneyball.app.use_cases.casting_interactor import CastingInteractor
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db


def get_player_roster_repository(db: AsyncSession = Depends(get_db)) -> PlayerRosterPort:
    return PlayerRosterRepository(session=db)


def get_casting_use_case(
    repository: PlayerRosterPort = Depends(get_player_roster_repository),
) -> CastingUseCase:
    return CastingInteractor(repository=repository)


__all__ = ["get_casting_use_case", "get_player_roster_repository"]
