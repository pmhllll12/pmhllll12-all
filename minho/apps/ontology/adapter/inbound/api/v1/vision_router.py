from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from ontology.adapter.inbound.api.schema.vision_schemas import (
    AnalyzedImageLogEntry,
    AnalyzeImageResponse,
)
from ontology.app.dtos.vision_dto import AnalyzeImageCommand
from ontology.app.ports.input.vision_use_case import VisionUseCase
from ontology.dependencies.vision_provider import get_vision_use_case

from core.matrix.vault_keymaker_secret_manager import MissingApiKeyError

image_analysis_router = APIRouter(tags=["vision"])

_MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10MB


@image_analysis_router.post("/analyze", response_model=AnalyzeImageResponse)
async def analyze_image(
    file: UploadFile = File(...),
    use_case: VisionUseCase = Depends(get_vision_use_case),
) -> AnalyzeImageResponse:
    """이미지를 업로드하면 Gemini 멀티모달로 설명·태그를 생성해 저장합니다."""
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(status_code=422, detail="이미지 파일만 업로드할 수 있습니다.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=422, detail="빈 파일입니다.")
    if len(content) > _MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="이미지 크기는 10MB를 초과할 수 없습니다.")

    try:
        result = await use_case.analyze(
            AnalyzeImageCommand(
                filename=file.filename or "unnamed",
                content=content,
                mime_type=file.content_type,
            )
        )
    except MissingApiKeyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return AnalyzeImageResponse(
        ok=result.ok,
        caption=result.caption,
        tags=result.tags,
        image_url=result.image_url,
        message=result.message,
    )


@image_analysis_router.get("/logs", response_model=list[AnalyzedImageLogEntry])
async def get_analyzed_logs(
    use_case: VisionUseCase = Depends(get_vision_use_case),
) -> list[AnalyzedImageLogEntry]:
    """분석된 이미지 로그를 최신순으로 반환합니다 (최대 100건)."""
    logs = await use_case.get_logs()
    return [
        AnalyzedImageLogEntry(
            analyzed_at=log.analyzed_at,
            filename=log.filename,
            caption=log.caption,
            tags=log.tags,
            image_url=log.image_url,
        )
        for log in logs
    ]
