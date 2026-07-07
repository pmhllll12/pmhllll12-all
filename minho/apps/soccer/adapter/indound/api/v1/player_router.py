from fastapi import APIRouter, Depends
from soccer.adapter.indound.api.schemas.player_schemas import PlayerCreateSchema, PlayerSchema
from soccer.app.dtos.player_dto import PlayerResponse
from soccer.app.ports.input.player_use_case import PlayerUseCase
from soccer.dependencies.player_provider import get_player_use_case

player_router = APIRouter(prefix="/players", tags=["players"])


@player_router.get("/myself", response_model=PlayerResponse)
async def introduce_myself(
    player: PlayerUseCase = Depends(get_player_use_case),
) -> PlayerResponse:
    return await player.introduce_myself(
        PlayerSchema(id=1, position="FW", jersey_number=7, team_id=1)
    )


@player_router.post("/", response_model=PlayerResponse)
async def create_player(
    body: PlayerCreateSchema,
    player: PlayerUseCase = Depends(get_player_use_case),
) -> PlayerResponse:
    return await player.create(body)
