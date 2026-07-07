from __future__ import annotations

import pytest
from silicon_valley.adapter.outbound.repositories.piper_bighetti_hr_repository import (
    BighettiHrRepository,
)
from silicon_valley.adapter.outbound.repositories.piper_dinesh_dash_repository import (
    DineshDashRepository,
)
from silicon_valley.adapter.outbound.repositories.piper_dunn_coo_repository import (
    DunnCooRepository,
)
from silicon_valley.adapter.outbound.repositories.piper_gilfoyle_system_repository import (
    GilfoyleSystemRepository,
)
from silicon_valley.adapter.outbound.repositories.piper_hendricks_ceo_repository import (
    HendricksCeoRepository,
)
from silicon_valley.app.dtos.piper_bighetti_hr_dto import BighettiHrQuery
from silicon_valley.app.dtos.piper_dinesh_dash_dto import DineshDashQuery
from silicon_valley.app.dtos.piper_dunn_coo_dto import DunnCooQuery
from silicon_valley.app.dtos.piper_gilfoyle_system_dto import GilfoyleSystemQuery
from silicon_valley.app.dtos.piper_hendricks_ceo_dto import HendricksCeoQuery

CASES = [
    (HendricksCeoRepository, HendricksCeoQuery),
    (DunnCooRepository, DunnCooQuery),
    (GilfoyleSystemRepository, GilfoyleSystemQuery),
    (DineshDashRepository, DineshDashQuery),
    (BighettiHrRepository, BighettiHrQuery),
]


@pytest.mark.anyio
@pytest.mark.parametrize("repository_cls, query_cls", CASES)
async def test_introduce_myself_passes_through_query(repository_cls, query_cls) -> None:
    # 레포지토리 구현이 session 을 실제로 쓰지 않는 데모 단계라 None 으로 충분
    repository = repository_cls(session=None)

    result = await repository.introduce_myself(
        query_cls(route="test-route", english_name="Test English", korean_name="테스트 한글")
    )

    assert result.route == "test-route"
    assert result.english_name == "Test English"
    assert result.korean_name == "테스트 한글"
