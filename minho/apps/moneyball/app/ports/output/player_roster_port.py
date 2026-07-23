from __future__ import annotations

from abc import ABC, abstractmethod

from moneyball.domain.entities.player_entity import PlayerEntity


class PlayerRosterPort(ABC):
    @abstractmethod
    async def get_players_by_team(self, team_id: str) -> list[PlayerEntity]:
        raise NotImplementedError


__all__ = ["PlayerRosterPort"]
