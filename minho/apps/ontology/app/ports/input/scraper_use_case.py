from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.scraper_dto import ScrapeCommand, ScrapeResult


class ScraperUseCase(ABC):
    @abstractmethod
    async def scrape(self, command: ScrapeCommand) -> ScrapeResult:
        raise NotImplementedError
