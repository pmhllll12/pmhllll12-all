from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FetchedPage:
    """WebPageFetcherPort가 반환하는 페이지 원시 데이터 — 제목·본문 텍스트·링크 목록."""

    url: str
    title: str
    text: str
    links: list[str]
