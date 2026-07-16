from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.domain.scraped_page import ScrapedPage


class ScrapeStoragePort(ABC):
    @abstractmethod
    async def save(self, website: str, keyword: str, pages: list[ScrapedPage]) -> str:
        """스크래핑 결과를 JSONL로 저장하고 저장 경로를 반환한다."""
        raise NotImplementedError
