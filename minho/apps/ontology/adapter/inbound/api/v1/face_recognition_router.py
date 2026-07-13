from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from ontology.adapter.inbound.api.schema.face_recognition_schemas import PredictFaceResponse
from ontology.app.dtos.face_recognition_dto import PredictFaceCommand
from ontology.app.ports.input.face_recognition_use_case import FaceRecognitionUseCase
from ontology.dependencies.face_recognition_provider import get_face_recognition_use_case

face_recognition_router = APIRouter(tags=["vision"])

_MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10MB


@face_recognition_router.post("/recognize-face", response_model=PredictFaceResponse)
async def recognize_face(
    file: UploadFile = File(...),
    use_case: FaceRecognitionUseCase = Depends(get_face_recognition_use_case),
) -> PredictFaceResponse:
    """얼굴 사진을 업로드하면 파인튜닝된 YOLO 분류 모델로 인물 이름을 예측합니다."""
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(status_code=422, detail="이미지 파일만 업로드할 수 있습니다.")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=422, detail="빈 파일입니다.")
    if len(content) > _MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="이미지 크기는 10MB를 초과할 수 없습니다.")

    try:
        result = await use_case.predict(
            PredictFaceCommand(
                content=content,
                filename=file.filename or "unnamed",
                mime_type=file.content_type,
            )
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return PredictFaceResponse(
        ok=result.ok,
        predicted_name=result.predicted_name,
        confidence=result.confidence,
        message=result.message,
    )
