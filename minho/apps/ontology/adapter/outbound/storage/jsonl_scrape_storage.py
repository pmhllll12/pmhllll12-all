from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from ontology.app.ports.output.scrape_storage_port import ScrapeStoragePort
from ontology.domain.scraped_page import ScrapedPage

_DEFAULT_DIR = Path(__file__).resolve().parents[3] / "resources" / "scraped"


def _website_slug(website: str) -> str:
    netloc = urlparse(website).netloc or website
    return netloc.replace(":", "_").replace(".", "_")


class JsonlScrapeStorageAdapter(ScrapeStoragePort):
    """스크래핑 결과를 resources/scraped/ 아래 JSONL 파일로 저장한다."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self._base_dir = base_dir or _DEFAULT_DIR

    async def save(self, website: str, keyword: str, pages: list[ScrapedPage]) -> str:
        return await asyncio.to_thread(self._save_sync, website, keyword, pages)

    def _save_sync(self, website: str, keyword: str, pages: list[ScrapedPage]) -> str:
        self._base_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{_website_slug(website)}_{datetime.now():%Y%m%d_%H%M%S}.jsonl"
        path = self._base_dir / filename
        with path.open("w", encoding="utf-8") as f:
            for page in pages:
                f.write(
                    json.dumps(
                        {
                            "website": website,
                            "keyword": keyword,
                            "url": page.url,
                            "matched": page.matched,
                            "title": page.title,
                            "snippet": page.snippet,
                            "scraped_at": page.scraped_at.isoformat(),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        return str(path)
