from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from silicon_valley.adapter.inbound.schema.piper_bighetti_hr_schema import (
    BighettiHrSchema,
)
from silicon_valley.adapter.inbound.schema.piper_dinesh_dash_schema import (
    DineshDashSchema,
)
from silicon_valley.adapter.inbound.schema.piper_dunn_coo_schema import DunnCooSchema
from silicon_valley.adapter.inbound.schema.piper_gilfoyle_system_schema import (
    GilfoyleSystemSchema,
)
from silicon_valley.adapter.inbound.schema.piper_hendricks_ceo_schema import (
    HendricksCeoSchema,
)
from silicon_valley.app.dtos.piper_bighetti_hr_dto import (
    BighettiHrQuery,
    BighettiHrResponse,
)
from silicon_valley.app.dtos.piper_dinesh_dash_dto import (
    DineshDashQuery,
    DineshDashResponse,
)
from silicon_valley.app.dtos.piper_dunn_coo_dto import DunnCooQuery, DunnCooResponse
from silicon_valley.app.dtos.piper_gilfoyle_system_dto import (
    GilfoyleSystemQuery,
    GilfoyleSystemResponse,
)
from silicon_valley.app.dtos.piper_hendricks_ceo_dto import (
    HendricksCeoQuery,
    HendricksCeoResponse,
)
from silicon_valley.app.use_cases.piper_bighetti_hr_interactor import (
    BighettiHrInteractor,
)
from silicon_valley.app.use_cases.piper_dinesh_dash_interactor import (
    DineshDashInteractor,
)
from silicon_valley.app.use_cases.piper_dunn_coo_interactor import DunnCooInteractor
from silicon_valley.app.use_cases.piper_gilfoyle_system_interactor import (
    GilfoyleSystemInteractor,
)
from silicon_valley.app.use_cases.piper_hendricks_ceo_interactor import (
    HendricksCeoInteractor,
)

CASES = [
    (HendricksCeoInteractor, HendricksCeoSchema, HendricksCeoQuery, HendricksCeoResponse),
    (DunnCooInteractor, DunnCooSchema, DunnCooQuery, DunnCooResponse),
    (GilfoyleSystemInteractor, GilfoyleSystemSchema, GilfoyleSystemQuery, GilfoyleSystemResponse),
    (DineshDashInteractor, DineshDashSchema, DineshDashQuery, DineshDashResponse),
    (BighettiHrInteractor, BighettiHrSchema, BighettiHrQuery, BighettiHrResponse),
]


@pytest.mark.anyio
@pytest.mark.parametrize("interactor_cls, schema_cls, query_cls, response_cls", CASES)
async def test_introduce_myself_delegates_to_repository(
    interactor_cls, schema_cls, query_cls, response_cls
) -> None:
    expected = response_cls(
        route="test-route", english_name="Test English", korean_name="테스트 한글"
    )
    repository = AsyncMock()
    repository.introduce_myself.return_value = expected

    interactor = interactor_cls(repository=repository)
    schema = schema_cls(
        route="test-route", english_name="Test English", korean_name="테스트 한글"
    )
    result = await interactor.introduce_myself(schema)

    repository.introduce_myself.assert_awaited_once_with(
        query_cls(route="test-route", english_name="Test English", korean_name="테스트 한글")
    )
    assert result is expected
