from __future__ import annotations

import logging
from datetime import datetime

from admin.app.dtos.pdf_loader_dto import (
    PdfSummaryLog,
    PdfSummaryResult,
    UploadPdfCommand,
)
from admin.app.ports.input.pdf_loader_use_case import PdfLoaderUseCase
from admin.app.ports.output.pdf_loader_port import PdfLoaderPort
from admin.app.ports.output.pdf_summarizer_port import PdfSummarizerPort
from admin.app.ports.output.pdf_text_extractor_port import PdfTextExtractorPort
from admin.domain.entities.pdf_document_entity import PdfDocumentEntity

logger = logging.getLogger(__name__)


class PdfLoaderInteractor(PdfLoaderUseCase):
    def __init__(
        self,
        repository: PdfLoaderPort,
        extractor: PdfTextExtractorPort,
        summarizer: PdfSummarizerPort,
    ) -> None:
        self.repository = repository
        self.extractor = extractor
        self.summarizer = summarizer

    async def upload_and_summarize(self, command: UploadPdfCommand) -> PdfSummaryResult:
        text = await self.extractor.extract(command.content, command.filename)
        if not text.strip():
            raise ValueError("PDF에서 추출된 텍스트가 없습니다.")

        summary = await self.summarizer.summarize(text)

        document = PdfDocumentEntity(
            filename=command.filename,
            char_count=len(text),
            summary=summary,
            uploaded_at=datetime.now(),
        )
        await self.repository.save(
            filename=document.filename,
            char_count=document.char_count,
            summary=document.summary,
            uploaded_at=document.uploaded_at,
        )
        logger.info(
            "[PdfLoaderInteractor] upload_and_summarize filename=%r char_count=%d",
            document.filename,
            document.char_count,
        )
        return PdfSummaryResult(
            ok=True,
            filename=document.filename,
            char_count=document.char_count,
            summary=document.summary,
        )

    async def get_logs(self) -> list[PdfSummaryLog]:
        return await self.repository.list_recent()
