from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SendSemanticChatCommand:
    message: str


@dataclass(frozen=True)
class SemanticChatResult:
    intent_label: str
    intent_confidence: float
    reply: str
    model: str
