from fastapi import APIRouter, Depends
from silicon_valley.adapter.inbound.schema.piper_gilfoyle_system_schema import GilfoyleSystemSchema
from silicon_valley.app.dtos.piper_gilfoyle_system_dto import GilfoyleSystemResponse
from silicon_valley.app.ports.input.piper_gilfoyle_system_use_case import GilfoyleSystemUseCase
from silicon_valley.dependencies.piper_gilfoyle_system_provider import get_gilfoyle_system_use_case

'''
Bertram Gilfoyle (버트럼 길포일)
파이드 파이퍼의 시스템 아키텍트. 냉소적이고 까칠하지만 서버 인프라는 누구보다 철저히 지킨다.

추천 파일명: piper_gilfoyle_system_router.py
'''
gilfoyle_system_router = APIRouter(prefix="/gilfoyle", tags=["gilfoyle"])

@gilfoyle_system_router.get("/myself")
async def introduce_myself(
    gilfoyle: GilfoyleSystemUseCase = Depends(get_gilfoyle_system_use_case)
) -> GilfoyleSystemResponse :
    return await gilfoyle.introduce_myself(
        GilfoyleSystemSchema(
            route="gilfoyle",
            english_name="Bertram Gilfoyle",
            korean_name="버트럼 길포일",
        )
    )
