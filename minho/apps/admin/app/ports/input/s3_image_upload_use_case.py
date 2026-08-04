from __future__ import annotations

from abc import ABC, abstractmethod

from admin.app.dtos.receipt_ocr_dto import ReceiptOcrResult
from admin.app.dtos.s3_image_upload_dto import UploadedImageResult, UploadImageCommand


class S3ImageUploadUseCase(ABC):
    @abstractmethod
    async def upload(self, command: UploadImageCommand) -> UploadedImageResult:
        """이미지를 검증하고 저장한 뒤 조회 URL과 함께 결과를 돌려준다."""
        raise NotImplementedError


class ReceiptOcrUseCase(ABC):
    @abstractmethod
    async def list_receipts_with_ocr(self) -> list[ReceiptOcrResult]:
        """`receipts/` 폴더의 이미지를 나열하고 각각 OCR 텍스트를 붙여 돌려준다."""
        raise NotImplementedError
