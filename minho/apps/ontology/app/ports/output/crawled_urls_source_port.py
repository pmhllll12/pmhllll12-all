from __future__ import annotations

from abc import ABC, abstractmethod


class CrawledUrlsSourcePort(ABC):
    @abstractmethod
    async def get_latest_urls(self, website: str) -> list[str]:
        """website에 대해 가장 최근에 저장된 크롤링 결과의 URL 목록을 반환한다 (없으면 빈 리스트)."""
        raise NotImplementedError
