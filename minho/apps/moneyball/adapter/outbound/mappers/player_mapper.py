from __future__ import annotations

from moneyball.adapter.outbound.orm.player_orm import PlayerOrm
from moneyball.domain.entities.player_entity import PlayerEntity


def player_entity_from_orm(orm: PlayerOrm) -> PlayerEntity:
    return PlayerEntity(
        player_id=orm.player_id,
        name=orm.player_name,
        position=orm.position,
        back_no=orm.back_no,
        team_id=orm.team_id,
    )


__all__ = ["player_entity_from_orm"]
