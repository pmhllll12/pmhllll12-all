from __future__ import annotations

import asyncio
from datetime import datetime

from ontology.app.dtos.vision_dto import AnalyzeImageCommand, StoredImage
from ontology.app.ports.output.image_captioning_port import ImageCaptioningPort
from ontology.app.ports.output.image_storage_port import ImageStoragePort
from ontology.app.ports.output.vision_port import VisionPort
from ontology.app.use_cases.vision_interactor import VisionInteractor


class _StubCaptioner(ImageCaptioningPort):
    def __init__(self, caption: str = "고양이 사진", tags: list[str] | None = None) -> None:
        self.caption_text = caption
        self.tags_list = tags if tags is not None else ["고양이", "동물"]
        self.calls = 0

    async def caption(self, content: bytes, mime_type: str) -> tuple[str, list[str]]:
        self.calls += 1
        return self.caption_text, self.tags_list


class _StubStorage(ImageStoragePort):
    def __init__(self, image_key: str = "vision/abc123-cat.jpg") -> None:
        self.image_key = image_key
        self.upload_calls = 0
        self.get_url_calls = 0

    async def upload(self, content: bytes, filename: str, mime_type: str) -> str:
        self.upload_calls += 1
        return self.image_key

    async def get_url(self, key: str) -> str:
        self.get_url_calls += 1
        return f"https://presigned.example.com/{key}"


class _StubRepository(VisionPort):
    def __init__(self) -> None:
        self.saved: list[dict] = []

    async def save(
        self,
        filename: str,
        caption: str,
        tags: list[str],
        image_key: str,
        analyzed_at: datetime,
    ) -> None:
        self.saved.append(
            {
                "filename": filename,
                "caption": caption,
                "tags": tags,
                "image_key": image_key,
                "analyzed_at": analyzed_at,
            }
        )

    async def list_recent(self, limit: int = 100) -> list[StoredImage]:
        return [
            StoredImage(
                analyzed_at=row["analyzed_at"].isoformat(),
                filename=row["filename"],
                caption=row["caption"],
                tags=row["tags"],
                image_key=row["image_key"],
            )
            for row in self.saved
        ]


def _make_interactor() -> tuple[VisionInteractor, _StubRepository, _StubCaptioner, _StubStorage]:
    repository = _StubRepository()
    captioner = _StubCaptioner()
    storage = _StubStorage()
    interactor = VisionInteractor(repository=repository, captioner=captioner, storage=storage)
    return interactor, repository, captioner, storage


def test_analyze_saves_key_and_returns_presigned_url():
    async def _run():
        interactor, repository, *_ = _make_interactor()
        result = await interactor.analyze(
            AnalyzeImageCommand(filename="cat.jpg", content=b"fake-bytes", mime_type="image/jpeg")
        )
        return repository, result

    repository, result = asyncio.run(_run())
    assert result.ok is True
    assert result.caption == "고양이 사진"
    assert result.image_url == "https://presigned.example.com/vision/abc123-cat.jpg"
    assert len(repository.saved) == 1
    assert repository.saved[0]["filename"] == "cat.jpg"
    assert repository.saved[0]["tags"] == ["고양이", "동물"]
    assert repository.saved[0]["image_key"] == "vision/abc123-cat.jpg"


def test_get_logs_returns_saved_entries_with_resolved_urls():
    async def _run():
        interactor, *_ = _make_interactor()
        await interactor.analyze(
            AnalyzeImageCommand(filename="dog.png", content=b"fake-bytes", mime_type="image/png")
        )
        return await interactor.get_logs()

    logs = asyncio.run(_run())
    assert len(logs) == 1
    assert logs[0].filename == "dog.png"
    assert logs[0].image_url == "https://presigned.example.com/vision/abc123-cat.jpg"


def test_analyze_calls_captioner_and_storage_once():
    async def _run():
        interactor, _, captioner, storage = _make_interactor()
        await interactor.analyze(
            AnalyzeImageCommand(filename="cat.jpg", content=b"fake-bytes", mime_type="image/jpeg")
        )
        return captioner, storage

    captioner, storage = asyncio.run(_run())
    assert captioner.calls == 1
    assert storage.upload_calls == 1
    assert storage.get_url_calls == 1
