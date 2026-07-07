from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from titanic.adapter.inbound.api.schemas.crew_hartley_violin_schemas import HartleyViolinSchema
from titanic.app.dtos.crew_hartley_violin_dto import HartleyViolinResponse
from titanic.app.ports.input.crew_hartley_violin_use_case import HartleyViolinUseCase
from titanic.app.ports.input.crew_walter_roaster_use_case import WalterRoasterUseCase
from titanic.dependencies.crew_hartley_violin_provider import get_hartley_violin_use_case
from titanic.dependencies.crew_walter_roaster_provider import get_walter_roaster_use_case

'''
왈리스 하틀리 (Wallace Hartley - 악단장)
배가 가라앉는 극도의 공포 속에서도 승객들을 진정시키기 위해 끝까지 찬송가 '내 주를 가까이 하게 함은(Nearer, My God, to Thee)'을 연주했던 악단장입니다. 영화에서 가장 눈물지게 만드는 명장면의 주인공입니다. 배경 작업(Background Worker)이나 알림/이벤트 스트리밍 라우터에 어울립니다.

추천 파일명: hartley_violin_router.py (Violin: 마지막까지 켜던 바이올린)
'''
hartley_violin_router = APIRouter(prefix="/hartley", tags=["hartley"])

@hartley_violin_router.get("/myself")
async def introduce_myself(
    hartley: HartleyViolinUseCase = Depends(get_hartley_violin_use_case)
) -> HartleyViolinResponse:
    return await hartley.introduce_myself(
        HartleyViolinSchema(
            id=3,
            name="왈리스 하틀리 (Wallace Hartley)"
        )
    )

@hartley_violin_router.get("/correlation-plot")
async def get_correlation_plot(
    hartley: HartleyViolinUseCase = Depends(get_hartley_violin_use_case),
    walter: WalterRoasterUseCase = Depends(get_walter_roaster_use_case),
) -> StreamingResponse:
    train_set = await walter.get_train_set()
    image_buffer = hartley.generate_correlation_plot(train_set)
    return StreamingResponse(image_buffer, media_type="image/png")
