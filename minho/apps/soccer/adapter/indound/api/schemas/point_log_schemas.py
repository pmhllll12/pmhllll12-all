from datetime import datetime

from pydantic import BaseModel, Field


class PointLogSchema(BaseModel):
    id: int = Field(0, description="Point log ID")
    user_id: int = Field(0, description="User ID (FK → USERS.id)")
    admin_id: int | None = Field(None, description="Admin ID (FK → ADMINS.id), None if system")
    amount: int = Field(0, description="Point change amount (positive: earn, negative: spend)")
    reason: str = Field("", description="Reason for point change")
    created_at: datetime = Field(..., description="Log creation time")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "user_id": 3,
                "admin_id": None,
                "amount": 200,
                "reason": "Correct prediction reward",
                "created_at": "2026-06-16T09:00:00Z",
            }
        }
    }


class PointLogCreateSchema(BaseModel):
    user_id: int
    amount: int
    reason: str = Field(..., min_length=1, max_length=200)


