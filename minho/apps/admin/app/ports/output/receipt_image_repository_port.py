"""S3 `receipts/` 폴더 읽기 전용 아웃바운드 포트.

`ImageStoragePort`(업로드·presigned URL 발급, 쓰기 경로)와 분리했다 — 이 포트는
이미 올라간 이미지를 나열하고 OCR용 원본 바이트를 읽어오는 읽기 경로만 안다.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from admin.app.dtos.receipt_ocr_dto import ReceiptImageRef


class ReceiptImageRepositoryPort(ABC):
    @abstractmethod
    async def list_receipts(self) -> list[ReceiptImageRef]:
        """`receipts/` 폴더의 이미지 메타데이터를 최신순으로 돌려준다."""
        raise NotImplementedError

    @abstractmethod
    async def download(self, key: str) -> tuple[bytes, str]:
        """이미지 원본 바이트와 content-type을 돌려준다."""
        raise NotImplementedError
