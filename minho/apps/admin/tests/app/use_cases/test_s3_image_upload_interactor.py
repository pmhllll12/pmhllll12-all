"""유스케이스는 저장소 구현을 모른다 — 가짜 포트 하나로 전부 검증된다.

AWS 자격증명도 네트워크도 필요 없다는 점이 포트/어댑터 분리의 실익이다.
"""

from __future__ import annotations

import pytest
from admin.app.dtos.s3_image_upload_dto import UploadImageCommand
from admin.app.ports.output.image_storage_port import (
    ImageStoragePort,
    ImageStorageUnavailableError,
)
from admin.app.use_cases.s3_image_upload_interactor import S3ImageUploadInteractor
from admin.domain.entities.s3_image_entity import MAX_IMAGE_BYTES, ImageUploadRejected

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 32


class FakeImageStorage(ImageStoragePort):
    def __init__(self, fail_with: Exception | None = None) -> None:
        self.uploads: list[tuple[str, str, int]] = []
        self._fail_with = fail_with

    async def upload(self, content: bytes, filename: str, content_type: str) -> str:
        if self._fail_with is not None:
            raise self._fail_with
        self.uploads.append((filename, content_type, len(content)))
        return f"admin/images/fixed-{filename}"

    async def generate_view_url(self, key: str) -> str:
        return f"https://example.test/{key}?sig=x"


def _command(**overrides) -> UploadImageCommand:
    values = {"filename": "cat.png", "content_type": "image/png", "content": PNG}
    values.update(overrides)
    return UploadImageCommand(**values)


@pytest.mark.anyio
async def test_upload_returns_key_and_url():
    storage = FakeImageStorage()
    interactor = S3ImageUploadInteractor(storage=storage)

    result = await interactor.upload(_command())

    assert result.ok is True
    assert result.key == "admin/images/fixed-cat.png"
    assert result.url.startswith("https://example.test/admin/images/fixed-cat.png")
    assert result.size_bytes == len(PNG)
    assert storage.uploads == [("cat.png", "image/png", len(PNG))]


@pytest.mark.anyio
async def test_disallowed_content_type_never_reaches_storage():
    """규칙 위반은 저장 전에 걸러야 한다 — 올린 뒤 거절하면 쓰레기 객체가 남는다."""
    storage = FakeImageStorage()
    interactor = S3ImageUploadInteractor(storage=storage)

    with pytest.raises(ImageUploadRejected):
        await interactor.upload(_command(content_type="application/pdf"))

    assert storage.uploads == []


@pytest.mark.anyio
async def test_empty_file_is_rejected():
    storage = FakeImageStorage()
    interactor = S3ImageUploadInteractor(storage=storage)

    with pytest.raises(ImageUploadRejected):
        await interactor.upload(_command(content=b""))

    assert storage.uploads == []


@pytest.mark.anyio
async def test_oversized_file_is_rejected():
    storage = FakeImageStorage()
    interactor = S3ImageUploadInteractor(storage=storage)

    with pytest.raises(ImageUploadRejected):
        await interactor.upload(_command(content=b"0" * (MAX_IMAGE_BYTES + 1)))

    assert storage.uploads == []


@pytest.mark.anyio
async def test_storage_failure_propagates_as_port_error():
    """어댑터가 botocore 예외를 포트 예외로 바꿔 던지는 계약을 유스케이스가 지킨다."""
    storage = FakeImageStorage(fail_with=ImageStorageUnavailableError("자격증명 없음"))
    interactor = S3ImageUploadInteractor(storage=storage)

    with pytest.raises(ImageStorageUnavailableError):
        await interactor.upload(_command())
