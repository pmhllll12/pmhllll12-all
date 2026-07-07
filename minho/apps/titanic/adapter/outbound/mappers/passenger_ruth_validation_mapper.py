from __future__ import annotations

from titanic.domain.entities.passenger_ruth_validation_entity import RuthValidationEntity


def ruth_validation_default_entity() -> RuthValidationEntity:
    return RuthValidationEntity()


__all__ = ["ruth_validation_default_entity"]
