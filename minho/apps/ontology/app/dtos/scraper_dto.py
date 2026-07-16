from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScrapeCommand:
    max_pages: int = 30


@dataclass(frozen=True)
class ScrapeResult:
    ok: bool
    website: str
    keyword: str
    pages_scanned: int
    matched_count: int
    output_path: str
