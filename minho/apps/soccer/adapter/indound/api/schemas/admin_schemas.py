from datetime import datetime

from pydantic import BaseModel, Field


class AdminSchema(BaseModel):
    id: int = Field(0, description="Admin ID")
    username: str = Field("", description="Admin username")
    role: str = Field("", description="Admin role: super | manager | viewer")
    created_at: datetime = Field(..., description="Account creation time")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "username": "admin01",
                "role": "super",
                "created_at": "2026-01-01T00:00:00Z",
            }
        }
    }


class AdminCreateSchema(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)
    role: str = Field("viewer", pattern="^(super|manager|viewer)$")



