from __future__ import annotations

from abc import ABC, abstractmethod

from admin.app.dtos.pdf_loader_dto import (
    PdfSummaryLog,
    PdfSummaryResult,
    UploadPdfCommand,
)


class PdfLoaderUseCase(ABC):
    @abstractmethod
    async def upload_and_summarize(self, command: UploadPdfCommand) -> PdfSummaryResult:
        """PDF에서 텍스트를 추출하고 요약한 뒤 저장한다."""
        raise NotImplementedError

    @abstractmethod
    async def get_logs(self) -> list[PdfSummaryLog]:
        """저장된 PDF 요약 이력을 조회한다."""
        raise NotImplementedError
