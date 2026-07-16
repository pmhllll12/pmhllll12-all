from __future__ import annotations

import os

import redis.asyncio as redis
from ontology.app.ports.output.target_source_port import TargetSourcePort
from ontology.app.ports.output.target_writer_port import TargetWriterPort
from ontology.domain.crawl_target import CrawlTarget, MissingCrawlTargetError

_DEFAULT_WEBSITE_KEY = "crawler:target:website"
_DEFAULT_KEYWORD_KEY = "crawler:target:keyword"


class RedisTargetAdapter(TargetSourcePort, TargetWriterPort):
    """Redis에 저장된 website/keyword 키쌍을 크롤링·스크래핑 대상으로 읽어온다."""

    def __init__(
        self,
        redis_url: str | None = None,
        website_key: str = _DEFAULT_WEBSITE_KEY,
        keyword_key: str = _DEFAULT_KEYWORD_KEY,
    ) -> None:
        self._redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._website_key = website_key
        self._keyword_key = keyword_key
        self._client: redis.Redis | None = None

    def _get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(self._redis_url, decode_responses=True)
        return self._client

    async def get_target(self) -> CrawlTarget:
        client = self._get_client()
        website = await client.get(self._website_key)
        keyword = await client.get(self._keyword_key)
        if not website or not keyword:
            raise MissingCrawlTargetError(
                f"Redis에 크롤링 대상이 없습니다 (key={self._website_key!r}, {self._keyword_key!r})"
            )
        return CrawlTarget(website=website, keyword=keyword)

    async def set_target(self, target: CrawlTarget) -> None:
        client = self._get_client()
        await client.set(self._website_key, target.website)
        await client.set(self._keyword_key, target.keyword)
