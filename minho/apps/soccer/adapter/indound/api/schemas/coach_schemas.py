
from pydantic import BaseModel, Field


class CoachSchema(BaseModel):
    id: int = Field(0, description="Coach ID (FK → PERSONS.id)")
    license_level: str | None = Field(None, description="License level: A | B | PRO")
    team_id: int | None = Field(None, description="Team ID (FK → TEAMS.id)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 10,
                "license_level": "PRO",
                "team_id": 2,
            }
        }
    }


class CoachCreateSchema(BaseModel):
    id: int = Field(..., description="PERSONS.id")
    license_level: str | None = Field(None, max_length=20)
    team_id: int | None = None



