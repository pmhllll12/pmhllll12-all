from datetime import datetime

from pydantic import BaseModel, Field


class NotificationSchema(BaseModel):
    id: int = Field(0, description="Notification ID")
    user_id: int = Field(0, description="User ID (FK → USERS.id)")
    type: str = Field("", description="Notification type: prediction_result | point_change | system")
    title: str = Field("", description="Notification title")
    content: str = Field("", description="Notification content")
    status: str = Field("unread", description="Status: unread | read")
    sent_at: datetime | None = Field(None, description="Time when notification was sent")
    created_at: datetime = Field(..., description="Notification creation time")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "user_id": 3,
                "type": "prediction_result",
                "title": "예측 결과 알림",
                "content": "홈팀 승리 예측이 적중했습니다! +200 포인트",
                "status": "unread",
                "sent_at": "2026-06-16T09:05:00Z",
                "created_at": "2026-06-16T09:05:00Z",
            }
        }
    }





class NotificationStatusUpdateSchema(BaseModel):
    status: str = Field(..., pattern="^(unread|read)$")
