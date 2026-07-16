from __future__ import annotations

import asyncio

from ontology.app.dtos.command_parser_dto import ParsedCommand
from ontology.app.dtos.crawler_dto import CrawlCommand, CrawlResult
from ontology.app.ports.input.crawler_use_case import CrawlerUseCase
from ontology.app.ports.output.command_parser_port import CommandParserPort
from ontology.app.ports.output.target_writer_port import TargetWriterPort
from ontology.app.use_cases.submit_crawl_interactor import SubmitCrawlInteractor
from ontology.domain.crawl_target import CrawlTarget


class _StubCommandParser(CommandParserPort):
    def __init__(self, parsed: ParsedCommand) -> None:
        self.parsed = parsed
        self.calls: list[tuple[str, str]] = []

    async def parse(self, website: str, command: str) -> ParsedCommand:
        self.calls.append((website, command))
        return self.parsed


class _StubTargetWriter(TargetWriterPort):
    def __init__(self) -> None:
        self.saved: list[CrawlTarget] = []

    async def set_target(self, target: CrawlTarget) -> None:
        self.saved.append(target)


class _StubCrawlerUseCase(CrawlerUseCase):
    def __init__(self, result: CrawlResult) -> None:
        self.result = result
        self.commands: list[CrawlCommand] = []

    async def crawl(self, command: CrawlCommand) -> CrawlResult:
        self.commands.append(command)
        return self.result


def test_submit_writes_parsed_target_and_runs_crawl_with_parsed_scope():
    parsed = ParsedCommand(keyword="파이썬", max_depth=3, max_pages=10)
    parser = _StubCommandParser(parsed)
    writer = _StubTargetWriter()
    expected_result = CrawlResult(
        ok=True,
        website="https://example.com",
        keyword="파이썬",
        pages_crawled=2,
        urls=["https://example.com", "https://example.com/a"],
        output_path="/resources/crawled/x.jsonl",
    )
    crawler_use_case = _StubCrawlerUseCase(expected_result)
    interactor = SubmitCrawlInteractor(
        command_parser=parser, target_writer=writer, crawler_use_case=crawler_use_case
    )

    result = asyncio.run(
        interactor.submit(website="https://example.com", command="파이썬 관련 페이지를 3단계까지 모아줘")
    )

    assert result is expected_result
    assert parser.calls == [("https://example.com", "파이썬 관련 페이지를 3단계까지 모아줘")]
    assert writer.saved == [CrawlTarget(website="https://example.com", keyword="파이썬")]
    assert crawler_use_case.commands == [CrawlCommand(max_depth=3, max_pages=10)]
