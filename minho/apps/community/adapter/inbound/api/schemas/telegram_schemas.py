from __future__ import annotations

from pydantic import BaseModel


class TelegramSchema(BaseModel):
    id: int
    name: str


class TelegramResponse(BaseModel):
    id: int
    name: str
    role: str
    channels: list[str]
    greeting: str


class TelegramSendRequest(BaseModel):
    chat_id: str = ""
    message: str = ""


class TelegramSendResponse(BaseModel):
    ok: bool
    message: str
