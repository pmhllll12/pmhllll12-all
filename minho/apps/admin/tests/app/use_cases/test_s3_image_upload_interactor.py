"""유스케이스는 저장소 구현을 모른다 — 가짜 포트 하나로 전부 검증된다.

AWS 자격증명도 네트워크도 필요 없다는 점이 포트/어댑터 분리의 실익이다.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from admin.app.dtos.receipt_ocr_dto import ReceiptImageRef
from admin.app.dtos.s3_image_upload_dto import UploadImageCommand
from admin.app.ports.output.image_storage_port import (
    ImageStoragePort,
    ImageStorageUnavailableError,
)
from admin.app.ports.output.receipt_image_repository_port import ReceiptImageRepositoryPort
from admin.app.ports.output.receipt_ocr_port import ReceiptOcrPort
from admin.app.use_cases.s3_image_upload_interactor import (
    ReceiptOcrInteractor,
    S3ImageUploadInteractor,
)
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


class FakeReceiptRepository(ReceiptImageRepositoryPort):
    def __init__(self, refs: list[ReceiptImageRef]) -> None:
        self._refs = refs
        self._content_by_key = {ref.key: (b"jpeg-bytes", "image/jpeg") for ref in refs}

    async def list_receipts(self) -> list[ReceiptImageRef]:
        return self._refs

    async def download(self, key: str) -> tuple[bytes, str]:
        return self._content_by_key[key]


class FakeReceiptOcr(ReceiptOcrPort):
    def __init__(self) -> None:
        self.calls: list[tuple[bytes, str]] = []

    async def extract_text(self, content: bytes, mime_type: str) -> str:
        self.calls.append((content, mime_type))
        return "스타벅스 강남점\n아메리카노 4,500원"


@pytest.mark.anyio
async def test_list_receipts_with_ocr_returns_text_per_image():
    refs = [
        ReceiptImageRef(
            key="receipts/900__20260131__171210.jpg",
            filename="900__20260131__171210.jpg",
            uploaded_at=datetime(2026, 1, 31, 17, 12, 10, tzinfo=UTC),
        )
    ]
    repository = FakeReceiptRepository(refs)
    ocr = FakeReceiptOcr()
    interactor = ReceiptOcrInteractor(receipts=repository, ocr=ocr)

    results = await interactor.list_receipts_with_ocr()

    assert len(results) == 1
    assert results[0].key == "receipts/900__20260131__171210.jpg"
    assert results[0].filename == "900__20260131__171210.jpg"
    assert results[0].ocr_text == "스타벅스 강남점\n아메리카노 4,500원"
    assert ocr.calls == [(b"jpeg-bytes", "image/jpeg")]


@pytest.mark.anyio
async def test_list_receipts_with_ocr_empty_folder_returns_empty_list():
    interactor = ReceiptOcrInteractor(receipts=FakeReceiptRepository([]), ocr=FakeReceiptOcr())

    results = await interactor.list_receipts_with_ocr()

    assert results == []
