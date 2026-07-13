from fastapi import APIRouter, Depends
from admin.adapter.inbound.schema.piper_dunn_coo_schema import DunnCooSchema
from admin.app.dtos.piper_dunn_coo_dto import DunnCooResponse
from admin.app.ports.input.piper_dunn_coo_use_case import DunnCooUseCase
from admin.dependencies.piper_dunn_coo_provider import get_dunn_coo_use_case

'''
Jared Dunn (자레드 던)
파이드 파이퍼의 COO. 헌신적이고 충성스러운 운영 책임자로 회사를 위해 무엇이든 내어준다.

추천 파일명: piper_dunn_coo_router.py
'''
dunn_coo_router = APIRouter(prefix="/dunn", tags=["dunn"])

@dunn_coo_router.get("/myself")
async def introduce_myself(
    dunn: DunnCooUseCase = Depends(get_dunn_coo_use_case)
) -> DunnCooResponse :
    return await dunn.introduce_myself(
        DunnCooSchema(
            route="dunn",
            english_name="Jared Dunn",
            korean_name="자레드 던",
        )
    )
