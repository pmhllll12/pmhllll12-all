from __future__ import annotations

import asyncio
import logging
import os
import uuid
from typing import Any

import boto3
from botocore.config import Config
from ontology.app.ports.output.image_storage_port import ImageStoragePort

logger = logging.getLogger(__name__)

_DEFAULT_REGION = "ap-northeast-2"
_DEFAULT_URL_EXPIRES_IN = 3600


class MissingS3ConfigError(RuntimeError):
    """VISION_S3_BUCKET 등 필수 설정이 없을 때."""


class S3ImageStorageClient(ImageStoragePort):
    """업로드된 이미지를 S3 버킷(`VISION_S3_BUCKET`)에 저장한다.

    버킷은 비공개로 유지하고, 조회 시점에 presigned URL을 발급한다.
    버킷 이름에 점(.)이 있으면 virtual-hosted-style HTTPS 요청에서 SSL 인증서
    불일치가 날 수 있어 path-style 주소 방식을 명시적으로 사용한다.
    """

    def __init__(
        self,
        bucket: str | None = None,
        region: str | None = None,
        url_expires_in: int | None = None,
    ) -> None:
        raw_bucket = bucket if bucket is not None else os.getenv("VISION_S3_BUCKET", "")
        raw_region = region if region is not None else os.getenv("AWS_REGION", _DEFAULT_REGION)
        self.bucket = raw_bucket.strip()
        self.region = raw_region.strip()
        self.url_expires_in = (
            url_expires_in
            if url_expires_in is not None
            else int(os.getenv("VISION_S3_URL_EXPIRES_IN", _DEFAULT_URL_EXPIRES_IN))
        )
        self._client: Any = None

    def _get_client(self) -> Any:
        if not self.bucket:
            raise MissingS3ConfigError(
                "VISION_S3_BUCKET 이 설정되지 않았습니다. minho/.env 에 버킷 이름을 넣으세요."
            )
        if self._client is None:
            self._client = boto3.client(
                "s3",
                region_name=self.region,
                config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
            )
        return self._client

    async def upload(self, content: bytes, filename: str, mime_type: str) -> str:
        key = f"vision/{uuid.uuid4().hex}-{filename}"
        await asyncio.to_thread(self._put_object, key, content, mime_type)
        logger.info("[S3ImageStorageClient] upload bucket=%s key=%s", self.bucket, key)
        return key

    async def get_url(self, key: str) -> str:
        return await asyncio.to_thread(self._generate_presigned_url, key)

    def _put_object(self, key: str, content: bytes, mime_type: str) -> None:
        self._get_client().put_object(
            Bucket=self.bucket, Key=key, Body=content, ContentType=mime_type
        )

    def _generate_presigned_url(self, key: str) -> str:
        return self._get_client().generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=self.url_expires_in,
        )
