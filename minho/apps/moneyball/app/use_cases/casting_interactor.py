from __future__ import annotations

import re

from moneyball.app.dtos.casting_dto import CastingQuery, CastingResponse, CastingSlot
from moneyball.app.ports.input.casting_use_case import CastingUseCase
from moneyball.app.ports.output.player_roster_port import PlayerRosterPort
from moneyball.domain.entities.player_entity import PlayerEntity

_FORMATION_PATTERN = re.compile(r"^(\d+)-(\d+)-(\d+)$")


class CastingInteractor(CastingUseCase):
    def __init__(self, repository: PlayerRosterPort) -> None:
        self.repository = repository

    async def cast(self, query: CastingQuery) -> CastingResponse:
        slot_counts = _parse_formation(query.formation)
        roster = await self.repository.get_players_by_team(query.team_id)

        by_position: dict[str, list[PlayerEntity]] = {}
        for player in roster:
            by_position.setdefault(player.position or "UNKNOWN", []).append(player)
        for players in by_position.values():
            players.sort(key=_sort_key)

        starters: list[CastingSlot] = []
        unfilled_positions: list[str] = []
        selected_ids: set[str] = set()

        for position, count in slot_counts.items():
            chosen = by_position.get(position, [])[:count]
            for player in chosen:
                starters.append(_to_slot(player))
                selected_ids.add(player.player_id)
            if len(chosen) < count:
                unfilled_positions.append(position)

        bench = [_to_slot(player) for player in roster if player.player_id not in selected_ids]

        return CastingResponse(
            team_id=query.team_id,
            formation=query.formation,
            starters=starters,
            unfilled_positions=unfilled_positions,
            bench=bench,
        )


def _parse_formation(formation: str) -> dict[str, int]:
    match = _FORMATION_PATTERN.match(formation.strip())
    if not match:
        raise ValueError(
            f"invalid formation format (expected 'DF-MF-FW', e.g. '4-4-2'): {formation!r}"
        )
    df, mf, fw = (int(part) for part in match.groups())
    return {"GK": 1, "DF": df, "MF": mf, "FW": fw}


def _sort_key(player: PlayerEntity) -> tuple[int, str]:
    # 성과 지표(골/어시스트/평점 등)가 아직 없어 쓰는 결정적 임시 정렬 기준 —
    # 실제 스탯/임베딩 기반 랭킹이 생기면 이 기준을 교체한다.
    return (player.back_no if player.back_no is not None else 10_000, player.player_id)


def _to_slot(player: PlayerEntity) -> CastingSlot:
    return CastingSlot(
        position=player.position or "UNKNOWN",
        player_id=player.player_id,
        player_name=player.name,
    )


__all__ = ["CastingInteractor"]
