from pydantic import BaseModel, Field


class TournamentGroupSchema(BaseModel):
    id: int = Field(0, description="Group ID")
    tournament_name: str = Field("", description="Tournament name")
    stage: str = Field("", description="Stage: group | round_of_16 | quarter | semi | final")
    name: str = Field("", description="Group name, e.g. Group A")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "tournament_name": "FIFA World Cup 2026",
                "stage": "group",
                "name": "Group A",
            }
        }
    }


class TournamentGroupCreateSchema(BaseModel):
    tournament_name: str = Field(..., min_length=1, max_length=100)
    stage: str = Field(..., max_length=30)
    name: str = Field(..., min_length=1, max_length=50)



