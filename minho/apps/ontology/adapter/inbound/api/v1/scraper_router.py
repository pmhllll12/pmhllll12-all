from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from ontology.adapter.inbound.api.schema.scraper_schemas import (
    ScrapeResponse,
    SubmitScrapeRequest,
)
from ontology.app.dtos.scraper_dto import ScrapeCommand
from ontology.app.ports.input.scraper_use_case import ScraperUseCase
from ontology.app.ports.input.submit_scrape_use_case import SubmitScrapeUseCase
from ontology.dependencies.crawler_provider import (
    get_scraper_use_case,
    get_submit_scrape_use_case,
)
from ontology.domain.crawl_target import MissingCrawlTargetError

from core.matrix.vault_keymaker_secret_manager import MissingApiKeyError

scrape_router = APIRouter(tags=["scraper"])


@scrape_router.post("/scrape", response_model=ScrapeResponse)
async def scrape(
    max_pages: int = 30,
    use_case: ScraperUseCase = Depends(get_scraper_use_case),
) -> ScrapeResponse:
    """Redis에 저장된 website/keyword로 크롤러가 모은 페이지(또는 단일 페이지)를 스크래핑해 JSONL로 저장합니다."""
    try:
        result = await use_case.scrape(ScrapeCommand(max_pages=max_pages))
    except MissingCrawlTargetError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return ScrapeResponse(
        ok=result.ok,
        website=result.website,
        keyword=result.keyword,
        pages_scanned=result.pages_scanned,
        matched_count=result.matched_count,
        output_path=result.output_path,
    )


@scrape_router.post("/scrape/submit", response_model=ScrapeResponse)
async def submit_scrape(
    body: SubmitScrapeRequest,
    use_case: SubmitScrapeUseCase = Depends(get_submit_scrape_use_case),
) -> ScrapeResponse:
    """사이트 주소 + 자연어 명령어를 Gemini로 해석해 Redis에 기록하고 스크래핑을 실행합니다."""
    try:
        result = await use_case.submit(website=body.website, command=body.command)
    except MissingApiKeyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except MissingCrawlTargetError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return ScrapeResponse(
        ok=result.ok,
        website=result.website,
        keyword=result.keyword,
        pages_scanned=result.pages_scanned,
        matched_count=result.matched_count,
        output_path=result.output_path,
    )
