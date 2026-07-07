from fastapi import APIRouter, Depends
from soccer.adapter.indound.api.schemas.notification_schemas import (
    NotificationSchema,
    NotificationStatusUpdateSchema,
)
from soccer.app.dtos.notification_dto import NotificationResponse
from soccer.app.ports.input.notification_use_case import NotificationUseCase
from soccer.dependencies.notification_provider import get_notification_use_case

notification_router = APIRouter(prefix="/notifications", tags=["notifications"])


@notification_router.get("/myself", response_model=NotificationResponse)
async def introduce_myself(
    notification: NotificationUseCase = Depends(get_notification_use_case),
) -> NotificationResponse:
    from datetime import datetime
    return await notification.introduce_myself(
        NotificationSchema(
            id=1,
            user_id=1,
            type="prediction_result",
            title="예측 결과 알림",
            content="홈팀 승리 예측이 적중했습니다! +200 포인트",
            status="unread",
            created_at=datetime.now(),
        )
    )


@notification_router.patch("/{notification_id}/status", response_model=NotificationResponse)
async def update_status(
    notification_id: int,
    body: NotificationStatusUpdateSchema,
    notification: NotificationUseCase = Depends(get_notification_use_case),
) -> NotificationResponse:
    return await notification.update_status(notification_id, body)
