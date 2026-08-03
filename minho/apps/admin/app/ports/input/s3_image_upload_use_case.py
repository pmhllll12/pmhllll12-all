from __future__ import annotations

from abc import ABC, abstractmethod

from admin.app.dtos.s3_image_upload_dto import UploadedImageResult, UploadImageCommand


class S3ImageUploadUseCase(ABC):
    @abstractmethod
    async def upload(self, command: UploadImageCommand) -> UploadedImageResult:
        """이미지를 검증하고 저장한 뒤 조회 URL과 함께 결과를 돌려준다."""
        raise NotImplementedError
