from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UploadImageCommand:
    """라우터가 `UploadFile`을 풀어서 넘기는 입력. app 계층은 HTTP를 모른다."""

    filename: str
    content_type: str
    content: bytes


@dataclass(frozen=True)
class UploadedImageResult:
    ok: bool
    key: str
    filename: str
    content_type: str
    size_bytes: int
    url: str
    uploaded_at: str
    message: str = "uploaded"
