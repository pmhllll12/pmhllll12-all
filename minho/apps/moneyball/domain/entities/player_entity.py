from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlayerEntity:
    player_id: str
    name: str | None
    position: str | None
    back_no: int | None
    team_id: str | None


__all__ = ["PlayerEntity"]
