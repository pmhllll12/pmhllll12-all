from datetime import datetime

from pydantic import BaseModel, Field


class PredictionSchema(BaseModel):
    id: int = Field(0, description="Prediction ID")
    user_id: int = Field(0, description="User ID (FK → USERS.id)")
    match_id: int = Field(0, description="Match ID (FK → MATCHES.id)")
    predicted_result: str = Field("", description="Predicted result: home | draw | away")
    bet_point: int = Field(0, description="Points wagered")
    is_rewarded: bool = Field(False, description="Whether reward has been given")
    created_at: datetime = Field(..., description="Prediction creation time")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "user_id": 3,
                "match_id": 7,
                "predicted_result": "home",
                "bet_point": 100,
                "is_rewarded": False,
                "created_at": "2026-06-14T12:00:00Z",
            }
        }
    }


class PredictionCreateSchema(BaseModel):
    match_id: int
    predicted_result: str = Field(..., pattern="^(home|draw|away)$")
    bet_point: int = Field(..., ge=1)



