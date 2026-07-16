from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.crawler_dto import CrawlResult


class SubmitCrawlUseCase(ABC):
    @abstractmethod
    async def submit(self, website: str, command: str) -> CrawlResult:
        raise NotImplementedError
