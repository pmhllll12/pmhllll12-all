from __future__ import annotations

from pydantic import BaseModel


class AnalyzeImageResponse(BaseModel):
    ok: bool
    caption: str
    tags: list[str]
    image_url: str
    message: str = "analyzed"


class AnalyzedImageLogEntry(BaseModel):
    analyzed_at: str
    filename: str
    caption: str
    tags: list[str]
    image_url: str
