from fastapi import APIRouter, Depends
from soccer.adapter.indound.api.schemas.point_log_schemas import (
    PointLogCreateSchema,
    PointLogSchema,
)
from soccer.app.dtos.point_log_dto import PointLogResponse
from soccer.app.ports.input.point_log_use_case import PointLogUseCase
from soccer.dependencies.point_log_provider import get_point_log_use_case

point_log_router = APIRouter(prefix="/point-logs", tags=["point-logs"])


@point_log_router.get("/myself", response_model=PointLogResponse)
async def introduce_myself(
    point_log: PointLogUseCase = Depends(get_point_log_use_case),
) -> PointLogResponse:
    from datetime import datetime
    return await point_log.introduce_myself(
        PointLogSchema(
            id=1,
            user_id=1,
            amount=200,
            reason="Correct prediction reward",
            created_at=datetime.now(),
        )
    )


@point_log_router.post("/", response_model=PointLogResponse)
async def create_point_log(
    body: PointLogCreateSchema,
    point_log: PointLogUseCase = Depends(get_point_log_use_case),
) -> PointLogResponse:
    return await point_log.create(body)
