from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CrawlCommand:
    max_depth: int = 2
    max_pages: int = 30


@dataclass(frozen=True)
class CrawlResult:
    ok: bool
    website: str
    keyword: str
    pages_crawled: int
    urls: list[str]
    output_path: str
