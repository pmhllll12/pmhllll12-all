from __future__ import annotations

from pydantic import BaseModel


class LangchainChatRequest(BaseModel):
    message: str


class LangchainChatResponse(BaseModel):
    reply: str
    model: str
