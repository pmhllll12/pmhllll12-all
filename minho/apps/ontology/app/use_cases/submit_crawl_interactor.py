from __future__ import annotations

import logging

from ontology.app.dtos.crawler_dto import CrawlCommand, CrawlResult
from ontology.app.ports.input.crawler_use_case import CrawlerUseCase
from ontology.app.ports.input.submit_crawl_use_case import SubmitCrawlUseCase
from ontology.app.ports.output.command_parser_port import CommandParserPort
from ontology.app.ports.output.target_writer_port import TargetWriterPort
from ontology.domain.crawl_target import CrawlTarget

logger = logging.getLogger(__name__)


class SubmitCrawlInteractor(SubmitCrawlUseCase):
    """website/자연어 명령어를 keyword·범위로 해석해 Redis에 기록한 뒤 크롤링을 실행한다."""

    def __init__(
        self,
        command_parser: CommandParserPort,
        target_writer: TargetWriterPort,
        crawler_use_case: CrawlerUseCase,
    ) -> None:
        self.command_parser = command_parser
        self.target_writer = target_writer
        self.crawler_use_case = crawler_use_case

    async def submit(self, website: str, command: str) -> CrawlResult:
        parsed = await self.command_parser.parse(website, command)
        await self.target_writer.set_target(CrawlTarget(website=website, keyword=parsed.keyword))
        logger.info(
            "[SubmitCrawlInteractor] website=%r command=%r -> keyword=%r max_depth=%d max_pages=%d",
            website,
            command,
            parsed.keyword,
            parsed.max_depth,
            parsed.max_pages,
        )
        return await self.crawler_use_case.crawl(
            CrawlCommand(max_depth=parsed.max_depth, max_pages=parsed.max_pages)
        )
