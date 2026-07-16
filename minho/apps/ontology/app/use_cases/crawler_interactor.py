from __future__ import annotations

import logging
from collections import deque
from datetime import datetime
from urllib.parse import urlparse

from ontology.app.dtos.crawler_dto import CrawlCommand, CrawlResult
from ontology.app.ports.input.crawler_use_case import CrawlerUseCase
from ontology.app.ports.output.crawl_storage_port import CrawlStoragePort
from ontology.app.ports.output.target_source_port import TargetSourcePort
from ontology.app.ports.output.web_page_fetcher_port import WebPageFetcherPort
from ontology.domain.crawled_page import CrawledPage

logger = logging.getLogger(__name__)


class CrawlerInteractor(CrawlerUseCase):
    """Redis에서 읽은 website에서 시작해 같은 도메인 내부 링크만 따라가며 URL을 수집한다."""

    def __init__(
        self,
        target_source: TargetSourcePort,
        fetcher: WebPageFetcherPort,
        storage: CrawlStoragePort,
    ) -> None:
        self.target_source = target_source
        self.fetcher = fetcher
        self.storage = storage

    async def crawl(self, command: CrawlCommand) -> CrawlResult:
        target = await self.target_source.get_target()
        domain = urlparse(target.website).netloc

        queue: deque[tuple[str, int]] = deque([(target.website, 0)])
        visited: set[str] = set()
        pages: list[CrawledPage] = []

        while queue and len(pages) < command.max_pages:
            url, depth = queue.popleft()
            if url in visited:
                continue
            visited.add(url)

            try:
                fetched = await self.fetcher.fetch(url)
            except Exception:
                logger.warning("[CrawlerInteractor] fetch 실패 url=%r", url, exc_info=True)
                continue

            same_domain_links = [
                link for link in fetched.links if urlparse(link).netloc == domain
            ]
            pages.append(
                CrawledPage(
                    url=url,
                    depth=depth,
                    links=same_domain_links,
                    crawled_at=datetime.now(),
                )
            )
            if depth < command.max_depth:
                for link in same_domain_links:
                    if link not in visited:
                        queue.append((link, depth + 1))

        output_path = await self.storage.save(website=target.website, pages=pages)
        logger.info(
            "[CrawlerInteractor] crawl website=%r pages=%d output=%r",
            target.website,
            len(pages),
            output_path,
        )
        return CrawlResult(
            ok=True,
            website=target.website,
            keyword=target.keyword,
            pages_crawled=len(pages),
            urls=[page.url for page in pages],
            output_path=output_path,
        )
