from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.domain.crawl_target import CrawlTarget


class TargetSourcePort(ABC):
    @abstractmethod
    async def get_target(self) -> CrawlTarget:
        """크롤링/스크래핑 대상(website, keyword)을 가져온다."""
        raise NotImplementedError
