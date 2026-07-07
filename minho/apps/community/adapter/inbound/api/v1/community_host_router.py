from __future__ import annotations

from fastapi import APIRouter, Depends

from community.adapter.inbound.api.schemas.community_host_schemas import (
    CommunityHostResponse,
    CommunityHostSchema,
)
from community.app.ports.input.community_host_use_case import CommunityHostUseCase
from community.dependencies.providers import get_community_host_use_case

community_host_router = APIRouter(prefix="/host", tags=["community-host"])


@community_host_router.get("/myself", response_model=CommunityHostResponse)
async def introduce_myself(
    use_case: CommunityHostUseCase = Depends(get_community_host_use_case),
) -> CommunityHostResponse:
    return await use_case.introduce_myself(
        CommunityHostSchema(id=1, name="커뮤니티 호스트")
    )
