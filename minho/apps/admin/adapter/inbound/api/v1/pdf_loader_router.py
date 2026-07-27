from __future__ import annotations

from admin.adapter.inbound.schema.pdf_loader_schema import (
    PdfSummaryLogEntry,
    PdfSummaryResponse,
)
from admin.app.dtos.pdf_loader_dto import UploadPdfCommand
from admin.app.ports.input.pdf_loader_use_case import PdfLoaderUseCase
from admin.dependencies.pdf_loader_provider import get_pdf_loader_use_case
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from core.matrix.vault_keymaker_secret_manager import MissingApiKeyError

pdf_loader_router = APIRouter(prefix="/pdf", tags=["pdf"])

_MAX_PDF_BYTES = 20 * 1024 * 1024  # 20MB


@pdf_loader_router.post(
    "/upload", response_model=PdfSummaryResponse, summary="PDF 업로드 → 텍스트 추출·요약"
)
async def upload_pdf(
    file: UploadFile = File(...),
    use_case: PdfLoaderUseCase = Depends(get_pdf_loader_use_case),
) -> PdfSummaryResponse:
    """PDF를 업로드하면 텍스트를 추출해 Gemini로 요약하고 결과를 저장합니다."""
    filename = file.filename or ""
    is_pdf_content_type = (file.content_type or "") == "application/pdf"
    is_pdf_extension = filename.lower().endswith(".pdf")
    if not (is_pdf_content_type or is_pdf_extension):
        raise HTTPException(status_code=422, detail="PDF 파일만 업로드할 수 있습니다.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=422, detail="빈 파일입니다.")
    if len(content) > _MAX_PDF_BYTES:
        raise HTTPException(status_code=413, detail="PDF 크기는 20MB를 초과할 수 없습니다.")

    try:
        result = await use_case.upload_and_summarize(
            UploadPdfCommand(filename=filename or "unnamed.pdf", content=content)
        )
    except MissingApiKeyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return PdfSummaryResponse(
        ok=result.ok,
        filename=result.filename,
        char_count=result.char_count,
        summary=result.summary,
        message=result.message,
    )


@pdf_loader_router.get(
    "/logs", response_model=list[PdfSummaryLogEntry], summary="PDF 요약 이력 조회"
)
async def get_pdf_logs(
    use_case: PdfLoaderUseCase = Depends(get_pdf_loader_use_case),
) -> list[PdfSummaryLogEntry]:
    """저장된 PDF 요약 이력을 최신순으로 반환합니다 (최대 100건)."""
    logs = await use_case.get_logs()
    return [
        PdfSummaryLogEntry(
            filename=log.filename,
            char_count=log.char_count,
            summary=log.summary,
            uploaded_at=log.uploaded_at,
        )
        for log in logs
    ]
