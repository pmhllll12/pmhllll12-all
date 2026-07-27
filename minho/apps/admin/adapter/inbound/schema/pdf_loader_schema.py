from __future__ import annotations

from pydantic import BaseModel


class PdfSummaryResponse(BaseModel):
    ok: bool
    filename: str
    char_count: int
    summary: str
    message: str = "summarized"


class PdfSummaryLogEntry(BaseModel):
    filename: str
    char_count: int
    summary: str
    uploaded_at: str
