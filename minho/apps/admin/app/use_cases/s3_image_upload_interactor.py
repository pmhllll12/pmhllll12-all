from __future__ import annotations

import logging
from datetime import datetime

from admin.app.dtos.receipt_ocr_dto import ReceiptOcrResult
from admin.app.dtos.s3_image_upload_dto import UploadedImageResult, UploadImageCommand
from admin.app.ports.input.s3_image_upload_use_case import (
    ReceiptOcrUseCase,
    S3ImageUploadUseCase,
)
from admin.app.ports.output.image_storage_port import ImageStoragePort
from admin.app.ports.output.receipt_image_repository_port import ReceiptImageRepositoryPort
from admin.app.ports.output.receipt_ocr_port import ReceiptOcrPort
from admin.domain.entities.s3_image_entity import S3ImageEntity, ensure_uploadable

logger = logging.getLogger(__name__)


class S3ImageUploadInteractor(S3ImageUploadUseCase):
    """검증 → 저장 → 조회 URL 발급 순서를 조율한다.

    `storage`가 S3인지 다른 무엇인지 모른다. 그래서 이 클래스의 테스트는
    가짜 포트 하나만 있으면 되고 AWS가 필요 없다.
    """

    def __init__(self, storage: ImageStoragePort) -> None:
        self.storage = storage

    async def upload(self, command: UploadImageCommand) -> UploadedImageResult:
        # 저장 전에 도메인 규칙으로 거른다 — 올린 뒤 검사하면 지워야 할 객체가 남는다.
        ensure_uploadable(
            filename=command.filename,
            content_type=command.content_type,
            size_bytes=len(command.content),
        )

        key = await self.storage.upload(
            content=command.content,
            filename=command.filename,
            content_type=command.content_type,
        )
        image = S3ImageEntity(
            key=key,
            filename=command.filename,
            content_type=command.content_type,
            size_bytes=len(command.content),
            uploaded_at=datetime.now(),
        )

        url = await self.storage.generate_view_url(image.key)
        logger.info(
            "[S3ImageUploadInteractor] upload key=%r filename=%r size=%d",
            image.key,
            image.filename,
            image.size_bytes,
        )
        return UploadedImageResult(
            ok=True,
            key=image.key,
            filename=image.filename,
            content_type=image.content_type,
            size_bytes=image.size_bytes,
            url=url,
            uploaded_at=image.uploaded_at.isoformat(),
        )


class ReceiptOcrInteractor(ReceiptOcrUseCase):
    """`receipts/` 폴더를 나열 → 각 이미지를 내려받아 OCR까지 조율한다.

    `receipts`·`ocr` 모두 포트라 실제 S3·Gemini 없이 가짜 포트로 테스트된다.
    """

    def __init__(self, receipts: ReceiptImageRepositoryPort, ocr: ReceiptOcrPort) -> None:
        self.receipts = receipts
        self.ocr = ocr

    async def list_receipts_with_ocr(self) -> list[ReceiptOcrResult]:
        refs = await self.receipts.list_receipts()
        results: list[ReceiptOcrResult] = []
        for ref in refs:
            content, content_type = await self.receipts.download(ref.key)
            text = await self.ocr.extract_text(content, content_type)
            results.append(
                ReceiptOcrResult(
                    key=ref.key,
                    filename=ref.filename,
                    uploaded_at=ref.uploaded_at.isoformat(),
                    ocr_text=text,
                )
            )
        logger.info("[ReceiptOcrInteractor] list_receipts_with_ocr count=%d", len(results))
        return results
