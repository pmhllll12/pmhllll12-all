from __future__ import annotations

from titanic.domain.entities.crew_walter_roaster_entity import WalterRoasterEntity


def walter_roaster_default_entity() -> WalterRoasterEntity:
    return WalterRoasterEntity()


__all__ = ["walter_roaster_default_entity"]
