from __future__ import annotations

import logging
import re
from datetime import datetime

from ontology.app.dtos.scraper_dto import ScrapeCommand, ScrapeResult
from ontology.app.ports.input.scraper_use_case import ScraperUseCase
from ontology.app.ports.output.crawled_urls_source_port import CrawledUrlsSourcePort
from ontology.app.ports.output.scrape_storage_port import ScrapeStoragePort
from ontology.app.ports.output.target_source_port import TargetSourcePort
from ontology.app.ports.output.web_page_fetcher_port import WebPageFetcherPort
from ontology.domain.scraped_page import ScrapedPage

logger = logging.getLogger(__name__)

_SNIPPET_RADIUS = 80


class ScraperInteractor(ScraperUseCase):
    """크롤러가 모은 URL(없으면 website 단일 페이지)에서 keyword가 포함된 본문을 추출한다."""

    def __init__(
        self,
        target_source: TargetSourcePort,
        crawled_urls_source: CrawledUrlsSourcePort,
        fetcher: WebPageFetcherPort,
        storage: ScrapeStoragePort,
    ) -> None:
        self.target_source = target_source
        self.crawled_urls_source = crawled_urls_source
        self.fetcher = fetcher
        self.storage = storage

    async def scrape(self, command: ScrapeCommand) -> ScrapeResult:
        target = await self.target_source.get_target()

        urls = await self.crawled_urls_source.get_latest_urls(target.website)
        if not urls:
            urls = [target.website]
        urls = urls[: command.max_pages]

        pages: list[ScrapedPage] = []
        for url in urls:
            try:
                fetched = await self.fetcher.fetch(url)
            except Exception:
                logger.warning("[ScraperInteractor] fetch 실패 url=%r", url, exc_info=True)
                continue

            snippet, matched = _find_snippet(fetched.text, target.keyword)
            pages.append(
                ScrapedPage(
                    url=url,
                    keyword=target.keyword,
                    matched=matched,
                    title=fetched.title,
                    snippet=snippet,
                    scraped_at=datetime.now(),
                )
            )

        matched_count = sum(1 for page in pages if page.matched)
        output_path = await self.storage.save(
            website=target.website, keyword=target.keyword, pages=pages
        )
        logger.info(
            "[ScraperInteractor] scrape website=%r keyword=%r scanned=%d matched=%d output=%r",
            target.website,
            target.keyword,
            len(pages),
            matched_count,
            output_path,
        )
        return ScrapeResult(
            ok=True,
            website=target.website,
            keyword=target.keyword,
            pages_scanned=len(pages),
            matched_count=matched_count,
            output_path=output_path,
        )


def _find_snippet(text: str, keyword: str) -> tuple[str, bool]:
    match = re.search(re.escape(keyword), text, re.IGNORECASE)
    if not match:
        return "", False
    start = max(0, match.start() - _SNIPPET_RADIUS)
    end = min(len(text), match.end() + _SNIPPET_RADIUS)
    return text[start:end].strip(), True
