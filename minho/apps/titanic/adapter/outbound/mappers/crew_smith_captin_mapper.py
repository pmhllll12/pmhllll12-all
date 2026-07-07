from __future__ import annotations

from titanic.domain.entities.crew_smith_captin_entity import SmithCaptinEntity


def smith_captin_default_entity() -> SmithCaptinEntity:
    return SmithCaptinEntity()


__all__ = ["smith_captin_default_entity"]
