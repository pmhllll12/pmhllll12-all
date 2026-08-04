"""`admin/images/receipts/` 폴더 읽기 전용 리포지토리.

`S3ImageStorageClient`(업로드·presigned URL 발급, 쓰기 경로)와 분리했다 — 이
파일은 이미 올라간 영수증 이미지를 나열하고 OCR에 쓸 원본 바이트를 읽어오는
읽기 경로만 안다. 버킷·자격증명 다루는 방식은 `S3ImageStorageClient`와 같다.

prefix는 `S3ImageStorageClient._KEY_PREFIX`("admin/images")의 하위 폴더인
`admin/images/receipts/`다 — 업로드 파이프라인이 실제로 쓰는 위치와 맞춘 것.
"""

from __future__ import annotations

import asyncio
import logging
import mimetypes
import os
from typing import Any

import boto3
from admin.app.dtos.receipt_ocr_dto import ReceiptImageRef
from admin.app.ports.output.image_storage_port import ImageStorageUnavailableError
from admin.app.ports.output.receipt_image_repository_port import ReceiptImageRepositoryPort
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

logger = logging.getLogger(__name__)

_DEFAULT_REGION = "ap-northeast-2"
_RECEIPTS_PREFIX = "admin/images/receipts/"


class S3ImageUploadRepository(ReceiptImageRepositoryPort):
    def __init__(self, bucket: str | None = None, region: str | None = None) -> None:
        raw_bucket = bucket if bucket is not None else self._bucket_from_env()
        raw_region = region if region is not None else os.getenv("AWS_REGION", _DEFAULT_REGION)
        self.bucket = raw_bucket.strip()
        self.region = raw_region.strip()
        self._client: Any = None

    @staticmethod
    def _bucket_from_env() -> str:
        return os.getenv("ADMIN_S3_BUCKET") or os.getenv("VISION_S3_BUCKET", "")

    def _get_client(self) -> Any:
        if not self.bucket:
            raise ImageStorageUnavailableError(
                "S3 버킷이 설정되지 않았습니다. minho/.env 에 ADMIN_S3_BUCKET "
                "(또는 VISION_S3_BUCKET)을 버킷 이름으로 넣으세요."
            )
        if self._client is None:
            self._client = boto3.client(
                "s3",
                region_name=self.region,
                config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
            )
        return self._client

    async def list_receipts(self) -> list[ReceiptImageRef]:
        return await asyncio.to_thread(self._list_receipts)

    def _list_receipts(self) -> list[ReceiptImageRef]:
        try:
            response = self._get_client().list_objects_v2(
                Bucket=self.bucket, Prefix=_RECEIPTS_PREFIX
            )
        except (NoCredentialsError, ClientError, BotoCoreError) as exc:
            raise self._as_unavailable(exc) from exc

        refs = [
            ReceiptImageRef(
                key=obj["Key"],
                filename=obj["Key"].rsplit("/", 1)[-1],
                uploaded_at=obj["LastModified"],
            )
            for obj in response.get("Contents", [])
            if not obj["Key"].endswith("/")  # 폴더 자체(prefix)는 제외
        ]
        refs.sort(key=lambda ref: ref.uploaded_at, reverse=True)
        return refs

    async def download(self, key: str) -> tuple[bytes, str]:
        return await asyncio.to_thread(self._download, key)

    def _download(self, key: str) -> tuple[bytes, str]:
        try:
            obj = self._get_client().get_object(Bucket=self.bucket, Key=key)
        except (NoCredentialsError, ClientError, BotoCoreError) as exc:
            raise self._as_unavailable(exc) from exc
        content = obj["Body"].read()
        content_type = obj.get("ContentType") or mimetypes.guess_type(key)[0] or "image/jpeg"
        return content, content_type

    def _as_unavailable(self, exc: Exception) -> ImageStorageUnavailableError:
        logger.warning("[S3ImageUploadRepository] S3 접근 실패: %s", exc)
        if isinstance(exc, NoCredentialsError):
            return ImageStorageUnavailableError(
                "AWS 자격증명을 찾을 수 없습니다. EC2 인스턴스에 IAM 역할을 연결하거나 "
                "AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY 를 설정하세요."
            )
        return ImageStorageUnavailableError(f"S3에 접근할 수 없습니다: {exc}")
