from __future__ import annotations

import logging

from ontology.app.dtos.scraper_dto import ScrapeCommand, ScrapeResult
from ontology.app.ports.input.scraper_use_case import ScraperUseCase
from ontology.app.ports.input.submit_scrape_use_case import SubmitScrapeUseCase
from ontology.app.ports.output.command_parser_port import CommandParserPort
from ontology.app.ports.output.target_writer_port import TargetWriterPort
from ontology.domain.crawl_target import CrawlTarget

logger = logging.getLogger(__name__)


class SubmitScrapeInteractor(SubmitScrapeUseCase):
    """website/자연어 명령어를 keyword로 해석해 Redis에 기록한 뒤 스크래핑을 실행한다."""

    def __init__(
        self,
        command_parser: CommandParserPort,
        target_writer: TargetWriterPort,
        scraper_use_case: ScraperUseCase,
    ) -> None:
        self.command_parser = command_parser
        self.target_writer = target_writer
        self.scraper_use_case = scraper_use_case

    async def submit(self, website: str, command: str) -> ScrapeResult:
        parsed = await self.command_parser.parse(website, command)
        await self.target_writer.set_target(CrawlTarget(website=website, keyword=parsed.keyword))
        logger.info(
            "[SubmitScrapeInteractor] website=%r command=%r -> keyword=%r max_pages=%d",
            website,
            command,
            parsed.keyword,
            parsed.max_pages,
        )
        return await self.scraper_use_case.scrape(ScrapeCommand(max_pages=parsed.max_pages))
