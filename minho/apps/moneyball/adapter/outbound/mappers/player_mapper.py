from __future__ import annotations

from moneyball.adapter.outbound.orm.player_orm import PlayerOrm
from moneyball.app.dtos.player_embedding_dto import PlayerProfile
from moneyball.domain.entities.player_entity import PlayerEntity


def player_entity_from_orm(orm: PlayerOrm) -> PlayerEntity:
    return PlayerEntity(
        player_id=orm.player_id,
        name=orm.player_name,
        position=orm.position,
        back_no=orm.back_no,
        team_id=orm.team_id,
    )


def player_profile_from_orm(orm: PlayerOrm, team_name: str | None) -> PlayerProfile:
    """임베딩 소스 텍스트용 프로필 — `team_name` 은 teams 조인 결과."""
    return PlayerProfile(
        player_id=orm.player_id,
        player_name=orm.player_name,
        e_player_name=orm.e_player_name,
        nickname=orm.nickname,
        position=orm.position,
        back_no=orm.back_no,
        nation=orm.nation,
        height=orm.height,
        weight=orm.weight,
        join_yyyy=orm.join_yyyy,
        team_name=team_name,
    )


__all__ = ["player_entity_from_orm", "player_profile_from_orm"]
