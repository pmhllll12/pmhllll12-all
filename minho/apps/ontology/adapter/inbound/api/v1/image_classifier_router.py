from __future__ import annotations

import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from ontology.adapter.inbound.api.schema.image_classifier_schemas import (
    ClassifyImageResponse,
    LabelScoreSchema,
)
from ontology.app.dtos.image_classifier_dto import (
    DEFAULT_CONFIDENCE_THRESHOLD,
    ClassifyImageCommand,
)
from ontology.app.ports.input.image_classifier_use_case import ImageClassifierUseCase
from ontology.app.use_cases.image_classifier_interactor import InvalidImageError
from ontology.dependencies.image_classifier_provider import get_image_classifier_use_case

image_classifier_router = APIRouter(tags=["vision"])

_MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10MB


def _get_confidence_threshold() -> float:
    raw = os.getenv("CLASSIFIER_CONFIDENCE_THRESHOLD")
    if not raw:
        return DEFAULT_CONFIDENCE_THRESHOLD
    try:
        return float(raw)
    except ValueError:
        return DEFAULT_CONFIDENCE_THRESHOLD


@image_classifier_router.post("/classify", response_model=ClassifyImageResponse)
async def classify_image(
    file: UploadFile = File(...),
    use_case: ImageClassifierUseCase = Depends(get_image_classifier_use_case),
) -> ClassifyImageResponse:
    """이미지를 업로드하면 ConvNeXt Nano(ImageNet-1k)로 분류한 top-5 라벨을 반환합니다."""
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(status_code=422, detail="이미지 파일만 업로드할 수 있습니다.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=422, detail="빈 파일입니다.")
    if len(content) > _MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="이미지 크기는 10MB를 초과할 수 없습니다.")

    try:
        result = await use_case.classify(
            ClassifyImageCommand(
                content=content,
                filename=file.filename or "unnamed",
                confidence_threshold=_get_confidence_threshold(),
            )
        )
    except InvalidImageError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return ClassifyImageResponse(
        ok=result.ok,
        label=result.label,
        confidence=result.confidence,
        top5=[LabelScoreSchema(label=i.label, confidence=i.confidence) for i in result.top5],
        uncertain=result.uncertain,
        inference_ms=result.inference_ms,
        message=result.message,
    )
