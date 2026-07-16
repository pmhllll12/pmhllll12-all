from __future__ import annotations

from pydantic import BaseModel


class SubmitScrapeRequest(BaseModel):
    website: str
    command: str


class ScrapeResponse(BaseModel):
    ok: bool
    website: str
    keyword: str
    pages_scanned: int
    matched_count: int
    output_path: str
