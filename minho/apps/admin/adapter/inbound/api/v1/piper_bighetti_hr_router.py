from fastapi import APIRouter, Depends
from admin.adapter.inbound.schema.piper_bighetti_hr_schema import BighettiHrSchema
from admin.app.dtos.piper_bighetti_hr_dto import BighettiHrResponse
from admin.app.ports.input.piper_bighetti_hr_use_case import BighettiHrUseCase
from admin.dependencies.piper_bighetti_hr_provider import get_bighetti_hr_use_case

'''
Nelson 'Big Head' Bighetti (넬슨 '빅헤드' 비게티)
실력보다 운으로 늘 좋은 자리를 차지하는 인물. 이번엔 어쩌다 인사(HR) 업무를 맡았다.

추천 파일명: piper_bighetti_hr_router.py
'''
bighetti_hr_router = APIRouter(prefix="/bighetti", tags=["bighetti"])

@bighetti_hr_router.get("/myself")
async def introduce_myself(
    bighetti: BighettiHrUseCase = Depends(get_bighetti_hr_use_case)
) -> BighettiHrResponse :
    return await bighetti.introduce_myself(
        BighettiHrSchema(
            route="bighetti",
            english_name="Nelson 'Big Head' Bighetti",
            korean_name="넬슨 '빅헤드' 비게티",
        )
    )
