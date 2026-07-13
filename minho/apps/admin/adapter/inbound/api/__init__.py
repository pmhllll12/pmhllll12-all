"""HTTP API adapters — Silicon Valley V1 라우터를 한 데 묶어 노출."""

from __future__ import annotations

from fastapi import APIRouter
from admin.adapter.inbound.api.v1.piper_bighetti_hr_router import (
    bighetti_hr_router as piper_bighetti_hr_router,
)
from admin.adapter.inbound.api.v1.piper_dinesh_dash_router import (
    dinesh_dash_router as piper_dinesh_dash_router,
)
from admin.adapter.inbound.api.v1.piper_dunn_coo_router import (
    dunn_coo_router as piper_dunn_coo_router,
)
from admin.adapter.inbound.api.v1.piper_gilfoyle_system_router import (
    gilfoyle_system_router as piper_gilfoyle_system_router,
)
from admin.adapter.inbound.api.v1.piper_hendricks_ceo_router import (
    hendricks_ceo_router as piper_hendricks_ceo_router,
)

silicon_valley_router = APIRouter(prefix="/api/v1", tags=["silicon_valley"])

_CHARACTERS = [
    {"route": "hendricks", "english_name": "Richard Hendricks", "korean_name": "리처드 헨드릭스"},
    {"route": "dunn", "english_name": "Jared Dunn", "korean_name": "자레드 던"},
    {"route": "gilfoyle", "english_name": "Bertram Gilfoyle", "korean_name": "버트럼 길포일"},
    {"route": "dinesh", "english_name": "Dinesh Chugtai", "korean_name": "디네시 추그타이"},
    {"route": "bighetti", "english_name": "Nelson 'Big Head' Bighetti", "korean_name": "넬슨 '빅헤드' 비게티"},
]


@silicon_valley_router.get("/", summary="실리콘밸리 API 안내")
async def silicon_valley_root() -> dict[str, object]:
    """`/api/v1` 아래 5명 캐릭터의 이름과 `/myself` 엔드포인트 목록."""
    return {
        "message": "Silicon Valley demo API",
        "characters": _CHARACTERS,
    }


silicon_valley_router.include_router(piper_hendricks_ceo_router)
silicon_valley_router.include_router(piper_dunn_coo_router)
silicon_valley_router.include_router(piper_gilfoyle_system_router)
silicon_valley_router.include_router(piper_dinesh_dash_router)
silicon_valley_router.include_router(piper_bighetti_hr_router)

__all__ = ["silicon_valley_router"]
