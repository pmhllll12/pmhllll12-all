from __future__ import annotations

from pydantic import BaseModel


class EmailHostSchema(BaseModel):
    id: int
    name: str


class EmailHostResponse(BaseModel):
    id: int
    name: str
    role: str
    features: list[str]
    greeting: str
