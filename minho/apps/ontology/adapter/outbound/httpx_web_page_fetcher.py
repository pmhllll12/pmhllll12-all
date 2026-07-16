from __future__ import annotations

from html.parser import HTMLParser
from urllib.parse import urljoin

import httpx
from ontology.app.dtos.web_fetch_dto import FetchedPage
from ontology.app.ports.output.web_page_fetcher_port import WebPageFetcherPort

_USER_AGENT = "Mozilla/5.0 (compatible; OntologyBot/1.0)"
_SKIP_TEXT_TAGS = {"script", "style"}


class _PageHTMLParser(HTMLParser):
    """HTML에서 <title>, 본문 텍스트, <a href> 링크(절대 URL)를 추출한다."""

    def __init__(self, base_url: str) -> None:
        super().__init__()
        self._base_url = base_url
        self.title = ""
        self.links: list[str] = []
        self._text_chunks: list[str] = []
        self._in_title = False
        self._skip_depth = 0

    @property
    def text(self) -> str:
        return " ".join(self._text_chunks)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(urljoin(self._base_url, href))
        elif tag == "title":
            self._in_title = True
        elif tag in _SKIP_TEXT_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag in _SKIP_TEXT_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        if self._in_title:
            self.title += data
        stripped = data.strip()
        if stripped:
            self._text_chunks.append(stripped)


class HttpxWebPageFetcher(WebPageFetcherPort):
    """httpx로 페이지를 가져오고 stdlib html.parser로 제목·본문·링크를 추출한다."""

    def __init__(self, timeout: float = 10.0) -> None:
        self._timeout = timeout

    async def fetch(self, url: str) -> FetchedPage:
        async with httpx.AsyncClient(follow_redirects=True, timeout=self._timeout) as client:
            response = await client.get(url, headers={"User-Agent": _USER_AGENT})
            response.raise_for_status()

        final_url = str(response.url)
        parser = _PageHTMLParser(base_url=final_url)
        parser.feed(response.text)
        return FetchedPage(
            url=final_url,
            title=parser.title.strip(),
            text=parser.text,
            links=parser.links,
        )
