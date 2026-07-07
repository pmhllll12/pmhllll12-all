from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserSchema(BaseModel):
    id: int = Field(0, description="User ID")
    email: str = Field("", description="User email")
    nickname: str = Field("", description="User nickname")
    current_point: int = Field(0, description="Current point balance")
    created_at: datetime = Field(..., description="Account creation time")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "nickname": "soccer_fan",
                "current_point": 500,
                "created_at": "2026-01-01T00:00:00Z",
            }
        }
    }


class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    nickname: str = Field(..., min_length=1, max_length=50)



