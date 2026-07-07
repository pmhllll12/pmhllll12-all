from fastapi import APIRouter, Depends
from soccer.adapter.indound.api.schemas.tournament_group_schemas import (
    TournamentGroupCreateSchema,
    TournamentGroupSchema,
)
from soccer.app.dtos.tournament_group_dto import TournamentGroupResponse
from soccer.app.ports.input.tournament_group_use_case import TournamentGroupUseCase
from soccer.dependencies.tournament_group_provider import get_tournament_group_use_case

tournament_group_router = APIRouter(prefix="/groups", tags=["groups"])


@tournament_group_router.get("/myself", response_model=TournamentGroupResponse)
async def introduce_myself(
    group: TournamentGroupUseCase = Depends(get_tournament_group_use_case),
) -> TournamentGroupResponse:
    return await group.introduce_myself(
        TournamentGroupSchema(
            id=1,
            tournament_name="FIFA World Cup 2026",
            stage="group",
            name="Group A",
        )
    )


@tournament_group_router.post("/", response_model=TournamentGroupResponse)
async def create_group(
    body: TournamentGroupCreateSchema,
    group: TournamentGroupUseCase = Depends(get_tournament_group_use_case),
) -> TournamentGroupResponse:
    return await group.create(body)
