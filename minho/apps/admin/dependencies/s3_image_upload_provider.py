"""조립 지점. 여기서만 구현체가 포트에 꽂힌다 — 라우터도 유스케이스도
`S3ImageStorageClient`라는 이름을 모른다."""

from __future__ import annotations

from admin.adapter.outbound.client.gemini_receipt_ocr_client import GeminiReceiptOcrClient
from admin.adapter.outbound.client.s3_image_storage_client import S3ImageStorageClient
from admin.adapter.outbound.repositories.s3_image_upload_repository import (
    S3ImageUploadRepository,
)
from admin.app.ports.input.s3_image_upload_use_case import (
    ReceiptOcrUseCase,
    S3ImageUploadUseCase,
)
from admin.app.ports.output.image_storage_port import ImageStoragePort
from admin.app.ports.output.receipt_image_repository_port import ReceiptImageRepositoryPort
from admin.app.ports.output.receipt_ocr_port import ReceiptOcrPort
from admin.app.use_cases.s3_image_upload_interactor import (
    ReceiptOcrInteractor,
    S3ImageUploadInteractor,
)
from fastapi import Depends


def get_image_storage_port() -> ImageStoragePort:
    return S3ImageStorageClient()


def get_s3_image_upload_use_case(
    storage: ImageStoragePort = Depends(get_image_storage_port),
) -> S3ImageUploadUseCase:
    return S3ImageUploadInteractor(storage=storage)


def get_receipt_image_repository() -> ReceiptImageRepositoryPort:
    return S3ImageUploadRepository()


def get_receipt_ocr_port() -> ReceiptOcrPort:
    return GeminiReceiptOcrClient()


def get_receipt_ocr_use_case(
    receipts: ReceiptImageRepositoryPort = Depends(get_receipt_image_repository),
    ocr: ReceiptOcrPort = Depends(get_receipt_ocr_port),
) -> ReceiptOcrUseCase:
    return ReceiptOcrInteractor(receipts=receipts, ocr=ocr)
