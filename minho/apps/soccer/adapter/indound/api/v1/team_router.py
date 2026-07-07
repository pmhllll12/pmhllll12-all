from fastapi import APIRouter, Depends
from soccer.adapter.indound.api.schemas.team_schemas import TeamCreateSchema, TeamSchema
from soccer.app.dtos.team_dto import TeamResponse
from soccer.app.ports.input.team_use_case import TeamUseCase
from soccer.dependencies.team_provider import get_team_use_case

team_router = APIRouter(prefix="/teams", tags=["teams"])


@team_router.get("/myself", response_model=TeamResponse)
async def introduce_myself(
    team: TeamUseCase = Depends(get_team_use_case),
) -> TeamResponse:
    return await team.introduce_myself(
        TeamSchema(id=1, name="South Korea", code="KOR", group_id=1)
    )


@team_router.post("/", response_model=TeamResponse)
async def create_team(
    body: TeamCreateSchema,
    team: TeamUseCase = Depends(get_team_use_case),
) -> TeamResponse:
    return await team.create(body)
