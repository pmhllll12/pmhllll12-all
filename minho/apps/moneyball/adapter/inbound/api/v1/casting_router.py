from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from moneyball.app.dtos.casting_dto import CastingQuery, CastingResponse
from moneyball.app.ports.input.casting_use_case import CastingUseCase
from moneyball.dependencies.casting_provider import get_casting_use_case

casting_router = APIRouter(prefix="/casting", tags=["moneyball-casting"])


@casting_router.get("/{team_id}")
async def cast_lineup(
    team_id: str,
    formation: str = Query("4-4-2", description="DF-MF-FW 형식(예: 4-4-2). GK 1명은 자동 포함"),
    use_case: CastingUseCase = Depends(get_casting_use_case),
) -> CastingResponse:
    try:
        return await use_case.cast(CastingQuery(team_id=team_id, formation=formation))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


__all__ = ["casting_router"]
