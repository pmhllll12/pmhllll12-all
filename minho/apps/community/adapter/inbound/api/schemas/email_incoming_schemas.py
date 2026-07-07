from __future__ import annotations

from pydantic import BaseModel, Field


class EmailIncomingRequest(BaseModel):
    subject: str
    from_: str | None = Field(default=None, alias="from")
    to: str | None = None
    body: str | None = None
    message_id: str | None = Field(default=None, alias="messageId")

    model_config = {"populate_by_name": True}


class EmailIncomingResponse(BaseModel):
    ok: bool
    message: str = "received"


class EmailIncomingLogEntry(BaseModel):
    received_at: str
    subject: str
    from_: str | None = Field(default=None, alias="from")
    to: str | None = None
    body: str | None = None
    message_id: str | None = Field(default=None, alias="messageId")

    model_config = {"populate_by_name": True}
