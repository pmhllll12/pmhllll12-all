from __future__ import annotations

import asyncio

from ontology.app.dtos.scraper_dto import ScrapeCommand
from ontology.app.dtos.web_fetch_dto import FetchedPage
from ontology.app.ports.output.crawled_urls_source_port import CrawledUrlsSourcePort
from ontology.app.ports.output.scrape_storage_port import ScrapeStoragePort
from ontology.app.ports.output.target_source_port import TargetSourcePort
from ontology.app.ports.output.web_page_fetcher_port import WebPageFetcherPort
from ontology.app.use_cases.scrper_interactor import ScraperInteractor
from ontology.domain.crawl_target import CrawlTarget
from ontology.domain.scraped_page import ScrapedPage


class _StubTargetSource(TargetSourcePort):
    def __init__(self, website: str = "https://example.com", keyword: str = "파이썬") -> None:
        self.website = website
        self.keyword = keyword

    async def get_target(self) -> CrawlTarget:
        return CrawlTarget(website=self.website, keyword=self.keyword)


class _StubCrawledUrlsSource(CrawledUrlsSourcePort):
    def __init__(self, urls: list[str]) -> None:
        self.urls = urls

    async def get_latest_urls(self, website: str) -> list[str]:
        return self.urls


class _StubFetcher(WebPageFetcherPort):
    def __init__(self, pages: dict[str, FetchedPage]) -> None:
        self.pages = pages

    async def fetch(self, url: str) -> FetchedPage:
        return self.pages[url]


class _StubStorage(ScrapeStoragePort):
    def __init__(self) -> None:
        self.saved: list[tuple[str, str, list[ScrapedPage]]] = []

    async def save(self, website: str, keyword: str, pages: list[ScrapedPage]) -> str:
        self.saved.append((website, keyword, pages))
        return f"/resources/scraped/{website}.jsonl"


def test_scrape_uses_crawled_urls_and_marks_matches():
    pages = {
        "https://example.com/a": FetchedPage(
            url="https://example.com/a", title="A", text="여기는 파이썬 강의입니다", links=[]
        ),
        "https://example.com/b": FetchedPage(
            url="https://example.com/b", title="B", text="여긴 관련 없음", links=[]
        ),
    }
    interactor = ScraperInteractor(
        target_source=_StubTargetSource(),
        crawled_urls_source=_StubCrawledUrlsSource(list(pages.keys())),
        fetcher=_StubFetcher(pages),
        storage=_StubStorage(),
    )

    result = asyncio.run(interactor.scrape(ScrapeCommand()))

    assert result.pages_scanned == 2
    assert result.matched_count == 1


def test_scrape_falls_back_to_website_when_no_crawled_urls():
    pages = {
        "https://example.com": FetchedPage(
            url="https://example.com", title="Home", text="파이썬 홈페이지", links=[]
        ),
    }
    interactor = ScraperInteractor(
        target_source=_StubTargetSource(),
        crawled_urls_source=_StubCrawledUrlsSource([]),
        fetcher=_StubFetcher(pages),
        storage=_StubStorage(),
    )

    result = asyncio.run(interactor.scrape(ScrapeCommand()))

    assert result.pages_scanned == 1
    assert result.matched_count == 1
