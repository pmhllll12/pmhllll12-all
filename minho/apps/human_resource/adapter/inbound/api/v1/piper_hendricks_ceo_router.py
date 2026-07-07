from fastapi import APIRouter, Depends
from silicon_valley.adapter.inbound.schema.piper_hendricks_ceo_schema import HendricksCeoSchema
from silicon_valley.app.dtos.piper_hendricks_ceo_dto import HendricksCeoResponse
from silicon_valley.app.ports.input.piper_hendricks_ceo_use_case import HendricksCeoUseCase
from silicon_valley.dependencies.piper_hendricks_ceo_provider import get_hendricks_ceo_use_case

'''
Richard Hendricks (리처드 헨드릭스)
파이드 파이퍼의 창업자 겸 CEO. 압축 알고리즘을 발명해 회사를 세웠지만 사람 다루는 일에는 늘 서툴다.

추천 파일명: piper_hendricks_ceo_router.py
'''
hendricks_ceo_router = APIRouter(prefix="/hendricks", tags=["hendricks"])

@hendricks_ceo_router.get("/myself")
async def introduce_myself(
    hendricks: HendricksCeoUseCase = Depends(get_hendricks_ceo_use_case)
) -> HendricksCeoResponse :
    return await hendricks.introduce_myself(
        HendricksCeoSchema(
            route="hendricks",
            english_name="Richard Hendricks",
            korean_name="리처드 헨드릭스",
        )
    )
