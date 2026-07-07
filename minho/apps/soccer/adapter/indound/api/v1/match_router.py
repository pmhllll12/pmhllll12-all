from fastapi import APIRouter, Depends
from soccer.adapter.indound.api.schemas.match_schemas import (
    MatchCreateSchema,
    MatchSchema,
    MatchScoreUpdateSchema,
)
from soccer.app.dtos.match_dto import MatchResponse
from soccer.app.ports.input.match_use_case import MatchUseCase
from soccer.dependencies.match_provider import get_match_use_case

match_router = APIRouter(prefix="/matches", tags=["matches"])


@match_router.get("/myself", response_model=MatchResponse)
async def introduce_myself(
    match: MatchUseCase = Depends(get_match_use_case),
) -> MatchResponse:
    from datetime import datetime
    return await match.introduce_myself(
        MatchSchema(
            id=1,
            kickoff_time=datetime(2026, 6, 15, 18, 0, 0),
            round="Group Stage MD1",
            venue="MetLife Stadium",
            home_team_id=1,
            away_team_id=2,
        )
    )


@match_router.post("/", response_model=MatchResponse)
async def create_match(
    body: MatchCreateSchema,
    match: MatchUseCase = Depends(get_match_use_case),
) -> MatchResponse:
    return await match.create(body)


@match_router.patch("/{match_id}/score", response_model=MatchResponse)
async def update_score(
    match_id: int,
    body: MatchScoreUpdateSchema,
    match: MatchUseCase = Depends(get_match_use_case),
) -> MatchResponse:
    return await match.update_score(match_id, body)
