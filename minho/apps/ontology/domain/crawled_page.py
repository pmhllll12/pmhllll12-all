from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CrawledPage:
    """크롤러가 방문한 페이지 한 건 — 같은 도메인 내부 링크 목록을 포함한다."""

    url: str
    depth: int
    links: list[str]
    crawled_at: datetime
