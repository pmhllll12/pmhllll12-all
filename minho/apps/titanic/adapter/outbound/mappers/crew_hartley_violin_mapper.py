from __future__ import annotations

from titanic.domain.entities.crew_hartley_violin_entity import HartleyViolinEntity


def hartley_violin_default_entity() -> HartleyViolinEntity:
    return HartleyViolinEntity()


__all__ = ["hartley_violin_default_entity"]
