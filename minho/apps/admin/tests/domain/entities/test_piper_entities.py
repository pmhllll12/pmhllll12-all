from __future__ import annotations

import pytest
from admin.domain.entities.piper_bighetti_hr_entity import BighettiHrEntity
from admin.domain.entities.piper_dinesh_dash_entity import DineshDashEntity
from admin.domain.entities.piper_dunn_coo_entity import DunnCooEntity
from admin.domain.entities.piper_gilfoyle_system_entity import (
    GilfoyleSystemEntity,
)
from admin.domain.entities.piper_hendricks_ceo_entity import (
    HendricksCeoEntity,
)

ENTITY_CLASSES = [
    HendricksCeoEntity,
    DunnCooEntity,
    GilfoyleSystemEntity,
    DineshDashEntity,
    BighettiHrEntity,
]


@pytest.mark.parametrize("entity_cls", ENTITY_CLASSES)
def test_entity_constructs_and_supports_equality(entity_cls: type) -> None:
    assert entity_cls() == entity_cls()
