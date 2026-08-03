"""`ImageStoragePort`의 S3 구현.

boto3·botocore가 등장하는 유일한 지점이다. app·domain 계층은 이 파일을 모른다.

버킷 이름은 `ADMIN_S3_BUCKET` → 없으면 `VISION_S3_BUCKET` 순으로 읽는다.
후자는 `ontology` 앱이 쓰던 이름인데, 현재 두 앱이 같은 버킷을 공유하므로
폴백으로 받아들여 설정을 두 번 하지 않게 했다. 버킷을 분리할 때 앞의 이름만
넣으면 된다.

**자격증명은 이 코드가 다루지 않는다.** boto3 기본 탐색 순서(환경변수 →
`~/.aws/credentials` → EC2 인스턴스 역할)를 그대로 따른다. 운영에서는 인스턴스
역할을 쓰는 것이 안전하다 — 장기 키를 `.env`에 두지 않아도 된다.
"""

from __future__ import annotations

import asyncio
import logging
import os
import uuid
from typing import Any

import boto3
from admin.app.ports.output.image_storage_port import (
    ImageStoragePort,
    ImageStorageUnavailableError,
)
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

logger = logging.getLogger(__name__)

_DEFAULT_REGION = "ap-northeast-2"
_DEFAULT_URL_EXPIRES_IN = 3600
_KEY_PREFIX = "admin/images"


class S3ImageStorageClient(ImageStoragePort):
    """이미지를 비공개 버킷에 넣고, 조회는 presigned URL로만 열어 준다.

    버킷 이름에 점(`.`)이 있으면 virtual-hosted-style HTTPS 요청에서 인증서가
    맞지 않을 수 있어 path-style 주소 방식을 명시한다.
    """

    def __init__(
        self,
        bucket: str | None = None,
        region: str | None = None,
        url_expires_in: int | None = None,
    ) -> None:
        raw_bucket = bucket if bucket is not None else self._bucket_from_env()
        raw_region = region if region is not None else os.getenv("AWS_REGION", _DEFAULT_REGION)
        self.bucket = raw_bucket.strip()
        self.region = raw_region.strip()
        self.url_expires_in = (
            url_expires_in
            if url_expires_in is not None
            else int(os.getenv("ADMIN_S3_URL_EXPIRES_IN", _DEFAULT_URL_EXPIRES_IN))
        )
        self._client: Any = None

    @staticmethod
    def _bucket_from_env() -> str:
        return os.getenv("ADMIN_S3_BUCKET") or os.getenv("VISION_S3_BUCKET", "")

    def _get_client(self) -> Any:
        if not self.bucket:
            raise ImageStorageUnavailableError(
                "S3 버킷이 설정되지 않았습니다. minho/.env 에 ADMIN_S3_BUCKET "
                "(또는 VISION_S3_BUCKET)을 ARN이 아닌 **버킷 이름**으로 넣으세요."
            )
        if self._client is None:
            self._client = boto3.client(
                "s3",
                region_name=self.region,
                config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
            )
        return self._client

    async def upload(self, content: bytes, filename: str, content_type: str) -> str:
        # 파일명을 그대로 키로 쓰면 같은 이름이 서로를 덮어쓴다. UUID를 앞에 붙여
        # 충돌을 없애고, 원래 이름은 사람이 알아볼 수 있게 뒤에 남긴다.
        key = f"{_KEY_PREFIX}/{uuid.uuid4().hex}-{filename}"
        await asyncio.to_thread(self._put_object, key, content, content_type)
        logger.info("[S3ImageStorageClient] upload bucket=%s key=%s", self.bucket, key)
        return key

    async def generate_view_url(self, key: str) -> str:
        return await asyncio.to_thread(self._generate_presigned_url, key)

    def _put_object(self, key: str, content: bytes, content_type: str) -> None:
        try:
            self._get_client().put_object(
                Bucket=self.bucket, Key=key, Body=content, ContentType=content_type
            )
        except (NoCredentialsError, ClientError, BotoCoreError) as exc:
            raise self._as_unavailable(exc) from exc

    def _generate_presigned_url(self, key: str) -> str:
        try:
            return self._get_client().generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket, "Key": key},
                ExpiresIn=self.url_expires_in,
            )
        except (NoCredentialsError, ClientError, BotoCoreError) as exc:
            raise self._as_unavailable(exc) from exc

    def _as_unavailable(self, exc: Exception) -> ImageStorageUnavailableError:
        """SDK 예외를 포트 예외로 옮긴다. 원인은 로그에 남기고, 밖으로는 조치 가능한
        문장만 내보낸다."""
        logger.warning("[S3ImageStorageClient] S3 접근 실패: %s", exc)
        if isinstance(exc, NoCredentialsError):
            return ImageStorageUnavailableError(
                "AWS 자격증명을 찾을 수 없습니다. EC2 인스턴스에 IAM 역할을 연결하거나 "
                "AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY 를 설정하세요."
            )
        return ImageStorageUnavailableError(f"S3에 접근할 수 없습니다: {exc}")
