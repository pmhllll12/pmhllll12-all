from fastapi import APIRouter, Depends
from soccer.adapter.indound.api.schemas.coach_schemas import CoachCreateSchema, CoachSchema
from soccer.app.dtos.coach_dto import CoachResponse
from soccer.app.ports.input.coach_use_case import CoachUseCase
from soccer.dependencies.coach_provider import get_coach_use_case

coach_router = APIRouter(prefix="/coaches", tags=["coaches"])


@coach_router.get("/myself", response_model=CoachResponse)
async def introduce_myself(
    coach: CoachUseCase = Depends(get_coach_use_case),
) -> CoachResponse:
    return await coach.introduce_myself(
        CoachSchema(id=1, license_level="PRO", team_id=1)
    )


@coach_router.post("/", response_model=CoachResponse)
async def create_coach(
    body: CoachCreateSchema,
    coach: CoachUseCase = Depends(get_coach_use_case),
) -> CoachResponse:
    return await coach.create(body)
