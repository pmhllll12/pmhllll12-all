from __future__ import annotations

from fastapi import APIRouter, Depends

from community.adapter.inbound.api.schemas.discord_schemas import DiscordResponse, DiscordSchema
from community.app.ports.input.discord_use_case import DiscordUseCase
from community.dependencies.providers import get_discord_use_case

discord_router = APIRouter(prefix="/discord", tags=["discord"])


@discord_router.get("/myself", response_model=DiscordResponse)
async def introduce_myself(
    use_case: DiscordUseCase = Depends(get_discord_use_case),
) -> DiscordResponse:
    return await use_case.introduce_myself(
        DiscordSchema(id=3, name="디스코드 관리자")
    )
