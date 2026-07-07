from __future__ import annotations

from titanic.domain.entities.passenger_isidor_couple_entity import IsidorCoupleEntity


def isidor_couple_default_entity() -> IsidorCoupleEntity:
    return IsidorCoupleEntity()


__all__ = ["isidor_couple_default_entity"]
