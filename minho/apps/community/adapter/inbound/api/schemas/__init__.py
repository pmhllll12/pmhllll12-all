from pydantic import BaseModel, Field


class EmailSendRequest(BaseModel):
    to_email: str = Field(..., description="수신자 이메일 주소")
    topic: str = Field(..., min_length=1, max_length=500, description="이메일 주제")


class EmailSendResponse(BaseModel):
    ok: bool
    message: str
