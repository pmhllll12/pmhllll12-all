
from pydantic import BaseModel, Field


class TeamSchema(BaseModel):
    id: int = Field(0, description="Team ID")
    name: str = Field("", description="Team name")
    code: str = Field("", description="Team code, e.g. KOR")
    group_id: int | None = Field(None, description="Group ID (FK → TOURNAMENT_GROUPS.id)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "South Korea",
                "code": "KOR",
                "group_id": 2,
            }
        }
    }


class TeamCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=2, max_length=10)
    group_id: int | None = None



