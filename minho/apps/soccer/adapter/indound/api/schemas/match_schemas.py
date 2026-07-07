from datetime import datetime

from pydantic import BaseModel, Field


class MatchSchema(BaseModel):
    id: int = Field(0, description="Match ID")
    kickoff_time: datetime = Field(..., description="Kickoff datetime (UTC)")
    round: str = Field("", description="Round name, e.g. Group Stage MD1")
    venue: str = Field("", description="Venue name")
    home_team_id: int = Field(0, description="Home team ID (FK → TEAMS.id)")
    away_team_id: int = Field(0, description="Away team ID (FK → TEAMS.id)")
    home_score: int | None = Field(None, description="Home team score")
    away_score: int | None = Field(None, description="Away team score")
    referee_id: int | None = Field(None, description="Referee ID (FK → REFEREES.id)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "kickoff_time": "2026-06-15T18:00:00Z",
                "round": "Group Stage MD1",
                "venue": "MetLife Stadium",
                "home_team_id": 1,
                "away_team_id": 2,
                "home_score": None,
                "away_score": None,
                "referee_id": 5,
            }
        }
    }


class MatchCreateSchema(BaseModel):
    kickoff_time: datetime
    round: str = Field(..., max_length=50)
    venue: str = Field(..., max_length=100)
    home_team_id: int
    away_team_id: int
    referee_id: int | None = None


class MatchScoreUpdateSchema(BaseModel):
    home_score: int = Field(..., ge=0)
    away_score: int = Field(..., ge=0)



