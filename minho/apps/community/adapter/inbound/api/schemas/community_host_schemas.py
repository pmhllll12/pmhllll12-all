from __future__ import annotations

from pydantic import BaseModel


class CommunityHostSchema(BaseModel):
    id: int
    name: str


class CommunityHostResponse(BaseModel):
    id: int
    name: str
    role: str
    channels: list[str]
    greeting: str
