from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AnalyzeImageCommand:
    filename: str
    content: bytes
    mime_type: str


@dataclass(frozen=True)
class AnalyzeImageResult:
    ok: bool
    caption: str
    tags: list[str]
    image_url: str
    message: str = "analyzed"


@dataclass(frozen=True)
class AnalyzedImageLog:
    analyzed_at: str
    filename: str
    caption: str
    tags: list[str]
    image_url: str


@dataclass(frozen=True)
class StoredImage:
    """저장소(repository)가 반환하는 원시 기록 — image_key는 아직 URL로 변환되지 않은
    S3 객체 키다. VisionInteractor가 ImageStoragePort로 presigned URL을 붙여
    AnalyzedImageLog로 변환한다."""

    analyzed_at: str
    filename: str
    caption: str
    tags: list[str]
    image_key: str
