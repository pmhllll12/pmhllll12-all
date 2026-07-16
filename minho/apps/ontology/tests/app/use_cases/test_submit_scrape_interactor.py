from __future__ import annotations

import asyncio

from ontology.app.dtos.command_parser_dto import ParsedCommand
from ontology.app.dtos.scraper_dto import ScrapeCommand, ScrapeResult
from ontology.app.ports.input.scraper_use_case import ScraperUseCase
from ontology.app.ports.output.command_parser_port import CommandParserPort
from ontology.app.ports.output.target_writer_port import TargetWriterPort
from ontology.app.use_cases.submit_scrape_interactor import SubmitScrapeInteractor
from ontology.domain.crawl_target import CrawlTarget


class _StubCommandParser(CommandParserPort):
    def __init__(self, parsed: ParsedCommand) -> None:
        self.parsed = parsed

    async def parse(self, website: str, command: str) -> ParsedCommand:
        return self.parsed


class _StubTargetWriter(TargetWriterPort):
    def __init__(self) -> None:
        self.saved: list[CrawlTarget] = []

    async def set_target(self, target: CrawlTarget) -> None:
        self.saved.append(target)


class _StubScraperUseCase(ScraperUseCase):
    def __init__(self, result: ScrapeResult) -> None:
        self.result = result
        self.commands: list[ScrapeCommand] = []

    async def scrape(self, command: ScrapeCommand) -> ScrapeResult:
        self.commands.append(command)
        return self.result


def test_submit_writes_parsed_target_and_runs_scrape_with_parsed_scope():
    parsed = ParsedCommand(keyword="파이썬", max_depth=2, max_pages=15)
    writer = _StubTargetWriter()
    expected_result = ScrapeResult(
        ok=True,
        website="https://example.com",
        keyword="파이썬",
        pages_scanned=3,
        matched_count=1,
        output_path="/resources/scraped/x.jsonl",
    )
    scraper_use_case = _StubScraperUseCase(expected_result)
    interactor = SubmitScrapeInteractor(
        command_parser=_StubCommandParser(parsed),
        target_writer=writer,
        scraper_use_case=scraper_use_case,
    )

    result = asyncio.run(
        interactor.submit(website="https://example.com", command="파이썬 관련 내용을 찾아줘")
    )

    assert result is expected_result
    assert writer.saved == [CrawlTarget(website="https://example.com", keyword="파이썬")]
    assert scraper_use_case.commands == [ScrapeCommand(max_pages=15)]
