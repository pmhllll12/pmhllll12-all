from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.crawler_dto import CrawlCommand, CrawlResult


class CrawlerUseCase(ABC):
    @abstractmethod
    async def crawl(self, command: CrawlCommand) -> CrawlResult:
        raise NotImplementedError
