from fastapi import APIRouter, Depends
from soccer.adapter.indound.api.schemas.referee_schemas import RefereeCreateSchema, RefereeSchema
from soccer.app.dtos.referee_dto import RefereeResponse
from soccer.app.ports.input.referee_use_case import RefereeUseCase
from soccer.dependencies.referee_provider import get_referee_use_case

referee_router = APIRouter(prefix="/referees", tags=["referees"])


@referee_router.get("/myself", response_model=RefereeResponse)
async def introduce_myself(
    referee: RefereeUseCase = Depends(get_referee_use_case),
) -> RefereeResponse:
    return await referee.introduce_myself(
        RefereeSchema(id=1, badge_year=2015)
    )


@referee_router.post("/", response_model=RefereeResponse)
async def create_referee(
    body: RefereeCreateSchema,
    referee: RefereeUseCase = Depends(get_referee_use_case),
) -> RefereeResponse:
    return await referee.create(body)
