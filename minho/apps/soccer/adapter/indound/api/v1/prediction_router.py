from fastapi import APIRouter, Depends
from soccer.adapter.indound.api.schemas.prediction_schemas import (
    PredictionCreateSchema,
    PredictionSchema,
)
from soccer.app.dtos.prediction_dto import PredictionResponse
from soccer.app.ports.input.prediction_use_case import PredictionUseCase
from soccer.dependencies.prediction_provider import get_prediction_use_case

prediction_router = APIRouter(prefix="/predictions", tags=["predictions"])


@prediction_router.get("/myself", response_model=PredictionResponse)
async def introduce_myself(
    prediction: PredictionUseCase = Depends(get_prediction_use_case),
) -> PredictionResponse:
    from datetime import datetime
    return await prediction.introduce_myself(
        PredictionSchema(
            id=1,
            user_id=1,
            match_id=1,
            predicted_result="home",
            bet_point=100,
            is_rewarded=False,
            created_at=datetime.now(),
        )
    )


@prediction_router.post("/", response_model=PredictionResponse)
async def create_prediction(
    body: PredictionCreateSchema,
    prediction: PredictionUseCase = Depends(get_prediction_use_case),
) -> PredictionResponse:
    return await prediction.create(body)
