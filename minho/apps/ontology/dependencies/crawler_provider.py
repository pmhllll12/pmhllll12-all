from __future__ import annotations

from fastapi import Depends
from ontology.adapter.outbound.gemini_command_parser import GeminiCommandParser
from ontology.adapter.outbound.httpx_web_page_fetcher import HttpxWebPageFetcher
from ontology.adapter.outbound.redis_target_adapter import RedisTargetAdapter
from ontology.adapter.outbound.storage.jsonl_crawl_storage import JsonlCrawlStorageAdapter
from ontology.adapter.outbound.storage.jsonl_scrape_storage import JsonlScrapeStorageAdapter
from ontology.app.ports.input.crawler_use_case import CrawlerUseCase
from ontology.app.ports.input.scraper_use_case import ScraperUseCase
from ontology.app.ports.input.submit_crawl_use_case import SubmitCrawlUseCase
from ontology.app.ports.input.submit_scrape_use_case import SubmitScrapeUseCase
from ontology.app.ports.output.command_parser_port import CommandParserPort
from ontology.app.ports.output.crawl_storage_port import CrawlStoragePort
from ontology.app.ports.output.crawled_urls_source_port import CrawledUrlsSourcePort
from ontology.app.ports.output.scrape_storage_port import ScrapeStoragePort
from ontology.app.ports.output.target_source_port import TargetSourcePort
from ontology.app.ports.output.target_writer_port import TargetWriterPort
from ontology.app.ports.output.web_page_fetcher_port import WebPageFetcherPort
from ontology.app.use_cases.crawler_interactor import CrawlerInteractor
from ontology.app.use_cases.scrper_interactor import ScraperInteractor
from ontology.app.use_cases.submit_crawl_interactor import SubmitCrawlInteractor
from ontology.app.use_cases.submit_scrape_interactor import SubmitScrapeInteractor

_crawl_storage = JsonlCrawlStorageAdapter()
_target_adapter = RedisTargetAdapter()


def get_target_source() -> TargetSourcePort:
    return _target_adapter


def get_target_writer() -> TargetWriterPort:
    return _target_adapter


def get_command_parser() -> CommandParserPort:
    return GeminiCommandParser()


def get_web_page_fetcher() -> WebPageFetcherPort:
    return HttpxWebPageFetcher()


def get_crawl_storage() -> CrawlStoragePort:
    return _crawl_storage


def get_crawled_urls_source() -> CrawledUrlsSourcePort:
    return _crawl_storage


def get_scrape_storage() -> ScrapeStoragePort:
    return JsonlScrapeStorageAdapter()


def get_crawler_use_case(
    target_source: TargetSourcePort = Depends(get_target_source),
    fetcher: WebPageFetcherPort = Depends(get_web_page_fetcher),
    storage: CrawlStoragePort = Depends(get_crawl_storage),
) -> CrawlerUseCase:
    return CrawlerInteractor(target_source=target_source, fetcher=fetcher, storage=storage)


def get_scraper_use_case(
    target_source: TargetSourcePort = Depends(get_target_source),
    crawled_urls_source: CrawledUrlsSourcePort = Depends(get_crawled_urls_source),
    fetcher: WebPageFetcherPort = Depends(get_web_page_fetcher),
    storage: ScrapeStoragePort = Depends(get_scrape_storage),
) -> ScraperUseCase:
    return ScraperInteractor(
        target_source=target_source,
        crawled_urls_source=crawled_urls_source,
        fetcher=fetcher,
        storage=storage,
    )


def get_submit_crawl_use_case(
    command_parser: CommandParserPort = Depends(get_command_parser),
    target_writer: TargetWriterPort = Depends(get_target_writer),
    crawler_use_case: CrawlerUseCase = Depends(get_crawler_use_case),
) -> SubmitCrawlUseCase:
    return SubmitCrawlInteractor(
        command_parser=command_parser,
        target_writer=target_writer,
        crawler_use_case=crawler_use_case,
    )


def get_submit_scrape_use_case(
    command_parser: CommandParserPort = Depends(get_command_parser),
    target_writer: TargetWriterPort = Depends(get_target_writer),
    scraper_use_case: ScraperUseCase = Depends(get_scraper_use_case),
) -> SubmitScrapeUseCase:
    return SubmitScrapeInteractor(
        command_parser=command_parser,
        target_writer=target_writer,
        scraper_use_case=scraper_use_case,
    )
