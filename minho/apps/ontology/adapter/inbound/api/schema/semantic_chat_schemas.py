from __future__ import annotations

from pydantic import BaseModel


class SemanticChatRequest(BaseModel):
    message: str


class SemanticChatResponse(BaseModel):
    reply: str
    model: str
    intent_label: str
    intent_confidence: float
