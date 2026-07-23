from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CastingQuery:
    team_id: str
    formation: str


@dataclass(frozen=True)
class CastingSlot:
    position: str
    player_id: str | None
    player_name: str | None


@dataclass(frozen=True)
class CastingResponse:
    team_id: str
    formation: str
    starters: list[CastingSlot]
    unfilled_positions: list[str]
    bench: list[CastingSlot]


__all__ = ["CastingQuery", "CastingResponse", "CastingSlot"]
