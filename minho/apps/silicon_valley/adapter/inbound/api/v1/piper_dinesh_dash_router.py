from fastapi import APIRouter, Depends
from silicon_valley.adapter.inbound.schema.piper_dinesh_dash_schema import DineshDashSchema
from silicon_valley.app.dtos.piper_dinesh_dash_dto import DineshDashResponse
from silicon_valley.app.ports.input.piper_dinesh_dash_use_case import DineshDashUseCase
from silicon_valley.dependencies.piper_dinesh_dash_provider import get_dinesh_dash_use_case

'''
Dinesh Chugtai (디네시 추그타이)
파이드 파이퍼의 엔지니어. 길포일과 늘 자존심 대결을 벌이는 코더.

추천 파일명: piper_dinesh_dash_router.py
'''
dinesh_dash_router = APIRouter(prefix="/dinesh", tags=["dinesh"])

@dinesh_dash_router.get("/myself")
async def introduce_myself(
    dinesh: DineshDashUseCase = Depends(get_dinesh_dash_use_case)
) -> DineshDashResponse :
    return await dinesh.introduce_myself(
        DineshDashSchema(
            route="dinesh",
            english_name="Dinesh Chugtai",
            korean_name="디네시 추그타이",
        )
    )
