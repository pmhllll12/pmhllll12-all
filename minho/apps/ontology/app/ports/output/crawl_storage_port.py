from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.domain.crawled_page import CrawledPage


class CrawlStoragePort(ABC):
    @abstractmethod
    async def save(self, website: str, pages: list[CrawledPage]) -> str:
        """크롤링 결과를 JSONL로 저장하고 저장 경로를 반환한다."""
        raise NotImplementedError
