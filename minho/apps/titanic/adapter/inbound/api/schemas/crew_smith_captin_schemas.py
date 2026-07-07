from pydantic import BaseModel, Field


class SmithCaptainSchema(BaseModel):
    id: int = Field(0, description="Captain ID")
    name: str = Field("에드워드 스미스", description="Captain's name")

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "탑승객이 몇 명이야?"
            }
        }
    }


class SmithChatRequest(BaseModel):
    """POST /smith/chat 본문 — 사용자 자연어."""

    message: str = Field(..., min_length=1, max_length=100_000)


class SmithChatResponse(BaseModel):
    """Gemini 가 생성한 선장 역할 답변."""

    reply: str
    model: str
