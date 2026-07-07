"""HTTP API adapters — Titanic V1 라우터를 한 데 묶어 노출."""

from __future__ import annotations

from fastapi import APIRouter
from titanic.adapter.inbound.api.V1.crew_andrews_architect_router import (
    andrews_architect_router as crew_andrews_architect_router,
)
from titanic.adapter.inbound.api.V1.crew_hartley_violin_router import (
    hartley_violin_router as crew_hartley_violin_router,
)
from titanic.adapter.inbound.api.V1.crew_james_director_router import (
    james_director_router as crew_james_director_router,
)
from titanic.adapter.inbound.api.V1.crew_lowe_boat_router import (
    lowe_boat_router as crew_lowe_boat_router,
)
from titanic.adapter.inbound.api.V1.crew_smith_captin_router import (
    smith_captain_router as crew_smith_captin_router,
)
from titanic.adapter.inbound.api.V1.crew_walter_roaster_router import (
    walter_roaster_router as crew_walter_roaster_router,
)
from titanic.adapter.inbound.api.V1.passenger_cal_tester_router import (
    cal_tester_router as passenger_cal_tester_router,
)
from titanic.adapter.inbound.api.V1.passenger_isidor_couple_router import (
    isidor_couple_router as passenger_isidor_couple_router,
)
from titanic.adapter.inbound.api.V1.passenger_jack_trainer_router import (
    jack_trainer_router as passenger_jack_trainer_router,
)
from titanic.adapter.inbound.api.V1.passenger_molly_scaler_router import (
    molly_scaler_router as passenger_molly_scaler_router,
)
from titanic.adapter.inbound.api.V1.passenger_rose_model_router import (
    rose_model_router as passenger_rose_model_router,
)
from titanic.adapter.inbound.api.V1.passenger_ruth_validation_router import (
    ruth_validation_router as passenger_ruth_validation_router,
)

# 레거시 별칭 (기존 `james_router` import 호환)
james_router = crew_james_director_router

titanic_router = APIRouter(prefix="/api/titanic", tags=["titanic"])


@titanic_router.get("/", summary="타이타닉 API 안내")
async def titanic_root() -> dict[str, str]:
    """`/titanic` 아래 캐릭터별 엔드포인트 목록(상위에 `/titanic` 한 번만 붙습니다)."""
    return {
        "message": "Titanic demo API",
        "paths": {
            "james_myself": "/api/titanic/james/myself",
            "james_upload": "/api/titanic/james/upload",
            "rose_myself": "/api/titanic/rose/myself",
            "walter_myself": "/api/titanic/walter/myself",
            "andrews_myself": "/api/titanic/andrews/myself",
            "cal_myself": "/api/titanic/cal/myself",
            "hartley_myself": "/api/titanic/hartley/myself",
            "lowe_myself": "/api/titanic/lowe/myself",
            "isidor_myself": "/api/titanic/isidor/myself",
            "jack_myself": "/api/titanic/jack/myself",
            "molly_myself": "/api/titanic/molly/myself",
            "ruth_myself": "/api/titanic/ruth/myself",
            "smith_myself": "/api/titanic/smith/myself",
            "smith_chat": "/api/titanic/smith/chat",
        },
    }

titanic_router.include_router(crew_james_director_router)
titanic_router.include_router(passenger_rose_model_router)
titanic_router.include_router(crew_walter_roaster_router)
titanic_router.include_router(crew_andrews_architect_router)
titanic_router.include_router(passenger_cal_tester_router)
titanic_router.include_router(crew_hartley_violin_router)
titanic_router.include_router(crew_lowe_boat_router)
titanic_router.include_router(passenger_isidor_couple_router)
titanic_router.include_router(passenger_jack_trainer_router)
titanic_router.include_router(passenger_molly_scaler_router)
titanic_router.include_router(passenger_ruth_validation_router)
titanic_router.include_router(crew_smith_captin_router)

__all__ = ["titanic_router", "james_router"]
