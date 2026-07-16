from __future__ import annotations

import asyncio

from ontology.app.dtos.crawler_dto import CrawlCommand
from ontology.app.dtos.web_fetch_dto import FetchedPage
from ontology.app.ports.output.crawl_storage_port import CrawlStoragePort
from ontology.app.ports.output.target_source_port import TargetSourcePort
from ontology.app.ports.output.web_page_fetcher_port import WebPageFetcherPort
from ontology.app.use_cases.crawler_interactor import CrawlerInteractor
from ontology.domain.crawl_target import CrawlTarget
from ontology.domain.crawled_page import CrawledPage


class _StubTargetSource(TargetSourcePort):
    def __init__(self, website: str = "https://example.com", keyword: str = "파이썬") -> None:
        self.website = website
        self.keyword = keyword

    async def get_target(self) -> CrawlTarget:
        return CrawlTarget(website=self.website, keyword=self.keyword)


class _StubFetcher(WebPageFetcherPort):
    def __init__(self, pages: dict[str, FetchedPage]) -> None:
        self.pages = pages
        self.calls: list[str] = []

    async def fetch(self, url: str) -> FetchedPage:
        self.calls.append(url)
        return self.pages[url]


class _StubStorage(CrawlStoragePort):
    def __init__(self) -> None:
        self.saved: list[tuple[str, list[CrawledPage]]] = []

    async def save(self, website: str, pages: list[CrawledPage]) -> str:
        self.saved.append((website, pages))
        return f"/resources/crawled/{website}.jsonl"


def _fetched(url: str, links: list[str]) -> FetchedPage:
    return FetchedPage(url=url, title="title", text="body", links=links)


def test_crawl_follows_only_same_domain_links():
    pages = {
        "https://example.com": _fetched(
            "https://example.com",
            links=["https://example.com/about", "https://other.com/x"],
        ),
        "https://example.com/about": _fetched("https://example.com/about", links=[]),
    }
    fetcher = _StubFetcher(pages)
    storage = _StubStorage()
    interactor = CrawlerInteractor(
        target_source=_StubTargetSource(), fetcher=fetcher, storage=storage
    )

    result = asyncio.run(interactor.crawl(CrawlCommand(max_depth=2, max_pages=10)))

    assert result.ok is True
    assert sorted(result.urls) == ["https://example.com", "https://example.com/about"]
    assert "https://other.com/x" not in fetcher.calls
    assert result.output_path == "/resources/crawled/https://example.com.jsonl"


def test_crawl_stops_at_max_pages():
    pages = {
        "https://example.com": _fetched(
            "https://example.com", links=["https://example.com/a", "https://example.com/b"]
        ),
        "https://example.com/a": _fetched("https://example.com/a", links=[]),
        "https://example.com/b": _fetched("https://example.com/b", links=[]),
    }
    fetcher = _StubFetcher(pages)
    storage = _StubStorage()
    interactor = CrawlerInteractor(
        target_source=_StubTargetSource(), fetcher=fetcher, storage=storage
    )

    result = asyncio.run(interactor.crawl(CrawlCommand(max_depth=2, max_pages=1)))

    assert result.pages_crawled == 1


def test_crawl_skips_urls_that_fail_to_fetch():
    class _FailingFetcher(WebPageFetcherPort):
        async def fetch(self, url: str) -> FetchedPage:
            raise RuntimeError("boom")

    storage = _StubStorage()
    interactor = CrawlerInteractor(
        target_source=_StubTargetSource(), fetcher=_FailingFetcher(), storage=storage
    )

    result = asyncio.run(interactor.crawl(CrawlCommand()))

    assert result.pages_crawled == 0
    assert result.urls == []
