
from pydantic import BaseModel, Field


class RefereeSchema(BaseModel):
    id: int = Field(0, description="Referee ID (FK → PERSONS.id)")
    badge_year: int | None = Field(None, description="Year of badge acquisition")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 20,
                "badge_year": 2015,
            }
        }
    }


class RefereeCreateSchema(BaseModel):
    id: int = Field(..., description="PERSONS.id")
    badge_year: int | None = Field(None, ge=1900, le=2100)



