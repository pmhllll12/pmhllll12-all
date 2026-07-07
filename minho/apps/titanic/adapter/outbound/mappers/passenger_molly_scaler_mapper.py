from __future__ import annotations

from titanic.domain.entities.passenger_molly_scaler_entity import MollyScalerEntity


def molly_scaler_default_entity() -> MollyScalerEntity:
    return MollyScalerEntity()


__all__ = ["molly_scaler_default_entity"]
