from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from ontology.adapter.inbound.api.schema.crawler_schemas import (
    CrawlResponse,
    SubmitCrawlRequest,
)
from ontology.app.dtos.crawler_dto import CrawlCommand
from ontology.app.ports.input.crawler_use_case import CrawlerUseCase
from ontology.app.ports.input.submit_crawl_use_case import SubmitCrawlUseCase
from ontology.dependencies.crawler_provider import (
    get_crawler_use_case,
    get_submit_crawl_use_case,
)
from ontology.domain.crawl_target import MissingCrawlTargetError

from core.matrix.vault_keymaker_secret_manager import MissingApiKeyError

crawl_router = APIRouter(tags=["crawler"])


@crawl_router.post("/crawl", response_model=CrawlResponse)
async def crawl(
    max_depth: int = 2,
    max_pages: int = 30,
    use_case: CrawlerUseCase = Depends(get_crawler_use_case),
) -> CrawlResponse:
    """Redis에 저장된 website에서 시작해 같은 도메인 내부 링크를 수집하고 JSONL로 저장합니다."""
    try:
        result = await use_case.crawl(CrawlCommand(max_depth=max_depth, max_pages=max_pages))
    except MissingCrawlTargetError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return CrawlResponse(
        ok=result.ok,
        website=result.website,
        keyword=result.keyword,
        pages_crawled=result.pages_crawled,
        urls=result.urls,
        output_path=result.output_path,
    )


@crawl_router.post("/crawl/submit", response_model=CrawlResponse)
async def submit_crawl(
    body: SubmitCrawlRequest,
    use_case: SubmitCrawlUseCase = Depends(get_submit_crawl_use_case),
) -> CrawlResponse:
    """사이트 주소 + 자연어 명령어를 Gemini로 해석해 Redis에 기록하고 크롤링을 실행합니다."""
    try:
        result = await use_case.submit(website=body.website, command=body.command)
    except MissingApiKeyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except MissingCrawlTargetError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return CrawlResponse(
        ok=result.ok,
        website=result.website,
        keyword=result.keyword,
        pages_crawled=result.pages_crawled,
        urls=result.urls,
        output_path=result.output_path,
    )
