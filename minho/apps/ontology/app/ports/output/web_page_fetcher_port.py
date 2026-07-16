from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.web_fetch_dto import FetchedPage


class WebPageFetcherPort(ABC):
    @abstractmethod
    async def fetch(self, url: str) -> FetchedPage:
        """URL의 페이지를 가져와 제목·본문 텍스트·페이지 내 링크 목록을 반환한다."""
        raise NotImplementedError
