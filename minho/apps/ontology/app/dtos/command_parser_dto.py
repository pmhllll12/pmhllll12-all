from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedCommand:
    """자연어 명령어에서 추출한 keyword와 크롤링 범위."""

    keyword: str
    max_depth: int
    max_pages: int
