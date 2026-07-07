from datetime import date

from pydantic import BaseModel, Field


class PersonSchema(BaseModel):
    id: int = Field(0, description="Person ID")
    name: str = Field("", description="Person's name")
    birth_date: date | None = Field(None, description="Date of birth")
    nationality: str | None = Field(None, description="Nationality")
    person_type: str = Field("", description="Type: player | coach | referee")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "name": "Son Heung-min",
                "birth_date": "1992-07-08",
                "nationality": "South Korea",
                "person_type": "player",
            }
        }
    }


class PersonCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    birth_date: date | None = None
    nationality: str | None = Field(None, max_length=50)
    person_type: str = Field(..., description="player | coach | referee")



