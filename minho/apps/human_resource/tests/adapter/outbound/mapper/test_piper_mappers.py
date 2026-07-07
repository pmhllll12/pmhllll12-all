from __future__ import annotations

from collections.abc import Callable

import pytest
from silicon_valley.adapter.outbound.mapper.piper_bighetti_hr_mapper import (
    bighetti_hr_default_entity,
)
from silicon_valley.adapter.outbound.mapper.piper_dinesh_dash_mapper import (
    dinesh_dash_default_entity,
)
from silicon_valley.adapter.outbound.mapper.piper_dunn_coo_mapper import (
    dunn_coo_default_entity,
)
from silicon_valley.adapter.outbound.mapper.piper_gilfoyle_system_mapper import (
    gilfoyle_system_default_entity,
)
from silicon_valley.adapter.outbound.mapper.piper_hendricks_ceo_mapper import (
    hendricks_ceo_default_entity,
)
from silicon_valley.domain.entities.piper_bighetti_hr_entity import BighettiHrEntity
from silicon_valley.domain.entities.piper_dinesh_dash_entity import DineshDashEntity
from silicon_valley.domain.entities.piper_dunn_coo_entity import DunnCooEntity
from silicon_valley.domain.entities.piper_gilfoyle_system_entity import (
    GilfoyleSystemEntity,
)
from silicon_valley.domain.entities.piper_hendricks_ceo_entity import (
    HendricksCeoEntity,
)

CASES: list[tuple[Callable[[], object], type]] = [
    (hendricks_ceo_default_entity, HendricksCeoEntity),
    (dunn_coo_default_entity, DunnCooEntity),
    (gilfoyle_system_default_entity, GilfoyleSystemEntity),
    (dinesh_dash_default_entity, DineshDashEntity),
    (bighetti_hr_default_entity, BighettiHrEntity),
]


@pytest.mark.parametrize("factory, entity_cls", CASES)
def test_default_entity_returns_entity_instance(
    factory: Callable[[], object], entity_cls: type
) -> None:
    assert isinstance(factory(), entity_cls)
