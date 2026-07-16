from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.scraper_dto import ScrapeResult


class SubmitScrapeUseCase(ABC):
    @abstractmethod
    async def submit(self, website: str, command: str) -> ScrapeResult:
        raise NotImplementedError
