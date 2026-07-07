
from pydantic import BaseModel, Field


class PlayerSchema(BaseModel):
    id: int = Field(0, description="Player ID (FK → PERSONS.id)")
    position: str | None = Field(None, description="Position: FW | MF | DF | GK")
    jersey_number: int | None = Field(None, description="Jersey number")
    team_id: int | None = Field(None, description="Team ID (FK → TEAMS.id)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "position": "FW",
                "jersey_number": 7,
                "team_id": 3,
            }
        }
    }


class PlayerCreateSchema(BaseModel):
    id: int = Field(..., description="PERSONS.id")
    position: str | None = Field(None, max_length=10)
    jersey_number: int | None = Field(None, ge=1, le=99)
    team_id: int | None = None


