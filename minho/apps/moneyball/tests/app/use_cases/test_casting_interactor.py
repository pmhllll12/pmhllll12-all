from __future__ import annotations

import asyncio

import pytest
from moneyball.app.dtos.casting_dto import CastingQuery
from moneyball.app.ports.output.player_roster_port import PlayerRosterPort
from moneyball.app.use_cases.casting_interactor import CastingInteractor
from moneyball.domain.entities.player_entity import PlayerEntity


class _StubRosterPort(PlayerRosterPort):
    def __init__(self, players: list[PlayerEntity]) -> None:
        self._players = players

    async def get_players_by_team(self, team_id: str) -> list[PlayerEntity]:
        return [p for p in self._players if p.team_id == team_id]


def _player(
    player_id: str, position: str, back_no: int | None, team_id: str = "K06"
) -> PlayerEntity:
    return PlayerEntity(
        player_id=player_id,
        name=f"선수{player_id}",
        position=position,
        back_no=back_no,
        team_id=team_id,
    )


def _run(coro):
    return asyncio.run(coro)


def test_full_roster_fills_every_slot():
    roster = [
        _player("gk1", "GK", 1),
        *[_player(f"df{i}", "DF", i) for i in range(1, 5)],
        *[_player(f"mf{i}", "MF", i) for i in range(1, 5)],
        *[_player(f"fw{i}", "FW", i) for i in range(1, 3)],
    ]
    interactor = CastingInteractor(repository=_StubRosterPort(roster))

    result = _run(interactor.cast(CastingQuery(team_id="K06", formation="4-4-2")))

    assert result.unfilled_positions == []
    assert len(result.starters) == 11
    assert {slot.position for slot in result.starters} == {"GK", "DF", "MF", "FW"}


def test_missing_goalkeeper_is_reported_as_unfilled():
    roster = [
        *[_player(f"df{i}", "DF", i) for i in range(1, 5)],
        *[_player(f"mf{i}", "MF", i) for i in range(1, 5)],
        *[_player(f"fw{i}", "FW", i) for i in range(1, 3)],
    ]
    interactor = CastingInteractor(repository=_StubRosterPort(roster))

    result = _run(interactor.cast(CastingQuery(team_id="K06", formation="4-4-2")))

    assert result.unfilled_positions == ["GK"]
    assert len(result.starters) == 10


def test_insufficient_position_players_partially_fills_and_reports_unfilled():
    roster = [
        _player("gk1", "GK", 1),
        *[_player(f"df{i}", "DF", i) for i in range(1, 3)],  # 2명뿐, 4명 필요
        *[_player(f"mf{i}", "MF", i) for i in range(1, 5)],
        *[_player(f"fw{i}", "FW", i) for i in range(1, 3)],
    ]
    interactor = CastingInteractor(repository=_StubRosterPort(roster))

    result = _run(interactor.cast(CastingQuery(team_id="K06", formation="4-4-2")))

    assert result.unfilled_positions == ["DF"]
    assert sum(1 for slot in result.starters if slot.position == "DF") == 2


def test_invalid_formation_raises_value_error():
    interactor = CastingInteractor(repository=_StubRosterPort([]))

    with pytest.raises(ValueError):
        _run(interactor.cast(CastingQuery(team_id="K06", formation="4-4")))

    with pytest.raises(ValueError):
        _run(interactor.cast(CastingQuery(team_id="K06", formation="a-b-c")))


def test_unselected_players_end_up_on_bench():
    roster = [
        _player("gk1", "GK", 1),
        *[_player(f"df{i}", "DF", i) for i in range(1, 6)],  # 5명, 4명만 선발
        *[_player(f"mf{i}", "MF", i) for i in range(1, 5)],
        *[_player(f"fw{i}", "FW", i) for i in range(1, 3)],
    ]
    interactor = CastingInteractor(repository=_StubRosterPort(roster))

    result = _run(interactor.cast(CastingQuery(team_id="K06", formation="4-4-2")))

    assert result.unfilled_positions == []
    bench_ids = {slot.player_id for slot in result.bench}
    assert bench_ids == {"df5"}
