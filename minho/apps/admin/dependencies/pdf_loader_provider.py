from __future__ import annotations

from admin.adapter.outbound.gemini_pdf_summarizer_client import GeminiPdfSummarizerClient
from admin.adapter.outbound.neo4j_graphrag_pdf_text_extractor import (
    Neo4jGraphRagPdfTextExtractor,
)
from admin.adapter.outbound.repositories.pdf_loader_repository import PdfLoaderRepository
from admin.app.ports.input.pdf_loader_use_case import PdfLoaderUseCase
from admin.app.ports.output.pdf_loader_port import PdfLoaderPort
from admin.app.ports.output.pdf_summarizer_port import PdfSummarizerPort
from admin.app.ports.output.pdf_text_extractor_port import PdfTextExtractorPort
from admin.app.use_cases.pdf_loader_interactor import PdfLoaderInteractor
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db


def get_pdf_loader_repository(db: AsyncSession = Depends(get_db)) -> PdfLoaderPort:
    return PdfLoaderRepository(session=db)


def get_pdf_text_extractor_port() -> PdfTextExtractorPort:
    return Neo4jGraphRagPdfTextExtractor()


def get_pdf_summarizer_port() -> PdfSummarizerPort:
    return GeminiPdfSummarizerClient()


def get_pdf_loader_use_case(
    repository: PdfLoaderPort = Depends(get_pdf_loader_repository),
    extractor: PdfTextExtractorPort = Depends(get_pdf_text_extractor_port),
    summarizer: PdfSummarizerPort = Depends(get_pdf_summarizer_port),
) -> PdfLoaderUseCase:
    return PdfLoaderInteractor(repository=repository, extractor=extractor, summarizer=summarizer)
