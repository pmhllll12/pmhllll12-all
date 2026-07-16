from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ScrapedPage:
    """스크래퍼가 keyword 매칭을 시도한 페이지 한 건."""

    url: str
    keyword: str
    matched: bool
    title: str
    snippet: str
    scraped_at: datetime
