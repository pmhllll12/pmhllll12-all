
"""이미지 업로드 인바운드 어댑터.

파이프라인:

    HTTP multipart
      → s3_image_upload_router (여기)          adapter/inbound
      → S3ImageUploadUseCase                   app/ports/input
      → S3ImageUploadInteractor                app/use_cases
      → ImageStoragePort                       app/ports/output
      → S3ImageStorageClient (boto3)           adapter/outbound

이 파일의 책임은 **HTTP를 app 계층의 언어로 옮기는 것**뿐이다. boto3도,
버킷 이름도, 키 생성 규칙도 여기서 알지 못한다.
"""

from __future__ import annotations

from admin.adapter.inbound.schema.s3_image_upload_schema import (
    ReceiptOcrResponse,
    S3ImageUploadResponse,
)
from admin.app.dtos.s3_image_upload_dto import UploadImageCommand
from admin.app.ports.input.s3_image_upload_use_case import (
    ReceiptOcrUseCase,
    S3ImageUploadUseCase,
)
from admin.app.ports.output.image_storage_port import ImageStorageUnavailableError
from admin.dependencies.s3_image_upload_provider import (
    get_receipt_ocr_use_case,
    get_s3_image_upload_use_case,
)
from admin.domain.entities.s3_image_entity import (
    ALLOWED_CONTENT_TYPES,
    MAX_IMAGE_BYTES,
    ImageUploadRejected,
)
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

s3_image_upload_router = APIRouter(prefix="/s3", tags=["s3"])


@s3_image_upload_router.post(
    "/images",
    response_model=S3ImageUploadResponse,
    summary="이미지 업로드 → S3 저장 후 조회 URL 반환",
)
async def upload_image(
    file: UploadFile = File(...),
    use_case: S3ImageUploadUseCase = Depends(get_s3_image_upload_use_case),
) -> S3ImageUploadResponse:
    """이미지를 비공개 버킷에 저장하고 임시 조회 URL을 돌려줍니다."""
    content = await file.read()

    # 상한을 넘긴 요청은 유스케이스까지 가기 전에 끊는다. 판정 기준값은 도메인이
    # 갖고 있어 라우터와 유스케이스가 서로 다른 숫자를 쓸 일이 없다.
    if len(content) > MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"이미지 크기는 {MAX_IMAGE_BYTES // (1024 * 1024)}MB를 초과할 수 없습니다.",
        )

    try:
        result = await use_case.upload(
            UploadImageCommand(
                filename=file.filename or "",
                content_type=file.content_type or "",
                content=content,
            )
        )
    except ImageUploadRejected as exc:
        # 도메인 규칙 위반 — 같은 요청을 다시 보내도 결과가 같다.
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ImageStorageUnavailableError as exc:
        # 저장소 설정·자격증명·장애. 클라이언트 잘못이 아니므로 503이다.
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return S3ImageUploadResponse(
        ok=result.ok,
        key=result.key,
        filename=result.filename,
        content_type=result.content_type,
        size_bytes=result.size_bytes,
        url=result.url,
        uploaded_at=result.uploaded_at,
        message=result.message,
    )


@s3_image_upload_router.get("/images/allowed-types", summary="업로드 가능한 이미지 형식·크기")
async def get_allowed_types() -> dict[str, object]:
    """프런트엔드가 업로드 전에 걸러낼 수 있도록 도메인 규칙을 그대로 노출합니다."""
    return {
        "allowed_content_types": sorted(ALLOWED_CONTENT_TYPES),
        "max_bytes": MAX_IMAGE_BYTES,
    }


@s3_image_upload_router.get(
    "/receipts",
    response_model=list[ReceiptOcrResponse],
    summary="receipts/ 폴더 영수증 이미지를 Gemini OCR로 읽어 반환",
)
async def get_receipts(
    use_case: ReceiptOcrUseCase = Depends(get_receipt_ocr_use_case),
) -> list[ReceiptOcrResponse]:
    """`receipts/` 폴더의 영수증 이미지를 나열하고 각각 OCR 텍스트를 붙여 돌려줍니다."""
    try:
        results = await use_case.list_receipts_with_ocr()
    except ImageStorageUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return [
        ReceiptOcrResponse(
            key=result.key,
            filename=result.filename,
            uploaded_at=result.uploaded_at,
            ocr_text=result.ocr_text,
        )
        for result in results
    ]
