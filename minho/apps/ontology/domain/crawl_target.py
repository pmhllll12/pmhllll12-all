from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CrawlTarget:
    """Redis 등 외부 저장소에서 읽어온 크롤링/스크래핑 대상."""

    website: str
    keyword: str


class MissingCrawlTargetError(RuntimeError):
    """크롤링/스크래핑 대상(website/keyword)을 찾을 수 없을 때."""
