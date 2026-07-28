from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SendChatMessageCommand:
    message: str


@dataclass(frozen=True)
class ChatMessageResult:
    reply: str
    model: str
