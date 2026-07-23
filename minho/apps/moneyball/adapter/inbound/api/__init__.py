from __future__ import annotations

from fastapi import APIRouter
from moneyball.adapter.inbound.api.v1.casting_router import casting_router

moneyball_router = APIRouter(prefix="/api/moneyball", tags=["moneyball"])
moneyball_router.include_router(casting_router)

__all__ = ["moneyball_router"]
