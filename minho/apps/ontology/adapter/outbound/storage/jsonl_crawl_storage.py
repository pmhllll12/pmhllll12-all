from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from ontology.app.ports.output.crawl_storage_port import CrawlStoragePort
from ontology.app.ports.output.crawled_urls_source_port import CrawledUrlsSourcePort
from ontology.domain.crawled_page import CrawledPage

_DEFAULT_DIR = Path(__file__).resolve().parents[3] / "resources" / "crawled"


def _website_slug(website: str) -> str:
    netloc = urlparse(website).netloc or website
    return netloc.replace(":", "_").replace(".", "_")


class JsonlCrawlStorageAdapter(CrawlStoragePort, CrawledUrlsSourcePort):
    """크롤링 결과를 resources/crawled/ 아래 JSONL 파일로 저장·조회한다."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self._base_dir = base_dir or _DEFAULT_DIR

    async def save(self, website: str, pages: list[CrawledPage]) -> str:
        return await asyncio.to_thread(self._save_sync, website, pages)

    async def get_latest_urls(self, website: str) -> list[str]:
        return await asyncio.to_thread(self._get_latest_urls_sync, website)

    def _save_sync(self, website: str, pages: list[CrawledPage]) -> str:
        self._base_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{_website_slug(website)}_{datetime.now():%Y%m%d_%H%M%S}.jsonl"
        path = self._base_dir / filename
        with path.open("w", encoding="utf-8") as f:
            for page in pages:
                f.write(
                    json.dumps(
                        {
                            "website": website,
                            "url": page.url,
                            "depth": page.depth,
                            "links": page.links,
                            "crawled_at": page.crawled_at.isoformat(),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        return str(path)

    def _get_latest_urls_sync(self, website: str) -> list[str]:
        candidates = sorted(self._base_dir.glob(f"{_website_slug(website)}_*.jsonl"))
        if not candidates:
            return []
        urls: list[str] = []
        with candidates[-1].open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                urls.append(json.loads(line)["url"])
        return urls
