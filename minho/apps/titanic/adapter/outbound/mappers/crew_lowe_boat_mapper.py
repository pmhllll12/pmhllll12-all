from __future__ import annotations

from titanic.domain.entities.crew_lowe_boat_entity import LoweBoatEntity


def lowe_boat_default_entity() -> LoweBoatEntity:
    return LoweBoatEntity()


__all__ = ["lowe_boat_default_entity"]
