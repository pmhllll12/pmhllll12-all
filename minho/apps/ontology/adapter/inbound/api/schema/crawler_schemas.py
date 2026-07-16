from __future__ import annotations

from pydantic import BaseModel


class SubmitCrawlRequest(BaseModel):
    website: str
    command: str


class CrawlResponse(BaseModel):
    ok: bool
    website: str
    keyword: str
    pages_crawled: int
    urls: list[str]
    output_path: str
