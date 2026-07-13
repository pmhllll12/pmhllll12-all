from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AnalyzedImage:
    filename: str
    caption: str
    tags: list[str]
    image_key: str
    analyzed_at: datetime

    def __post_init__(self) -> None:
        if not self.filename.strip():
            raise ValueError("filename은 비어 있을 수 없습니다.")
        if not self.caption.strip():
            raise ValueError("caption은 비어 있을 수 없습니다.")
        if not self.image_key.strip():
            raise ValueError("image_key는 비어 있을 수 없습니다.")
