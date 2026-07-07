from __future__ import annotations

from pydantic import BaseModel


class DiscordSchema(BaseModel):
    id: int
    name: str


class DiscordResponse(BaseModel):
    id: int
    name: str
    role: str
    channels: list[str]
    greeting: str
