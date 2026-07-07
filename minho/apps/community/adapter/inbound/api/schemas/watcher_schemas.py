from __future__ import annotations

from pydantic import BaseModel, Field


class WatcherIncomingRequest(BaseModel):
    channel: str = Field(..., description="인바운드 채널 (telegram, discord, email 등)")
    sender: str = Field(..., description="발신자")
    content: str = Field(..., min_length=1, description="메시지 본문")
    important_client: bool = Field(default=False, description="중요 거래처 여부")


class WatcherIncomingResponse(BaseModel):
    ok: bool
    route: str
    message: str


class WatcherJourneyLogEntry(BaseModel):
    received_at: str
    channel: str
    sender: str
    route: str
    steps: list[str]


class WatcherSchema(BaseModel):
    id: int
    name: str


class WatcherHostResponse(BaseModel):
    id: int
    name: str
    role: str
    features: list[str]
    greeting: str
