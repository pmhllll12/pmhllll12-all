from __future__ import annotations

from pydantic import BaseModel


class S3ImageUploadResponse(BaseModel):
    ok: bool
    key: str
    filename: str
    content_type: str
    size_bytes: int
    url: str
    uploaded_at: str
    message: str = "uploaded"
