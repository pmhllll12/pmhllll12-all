from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PdfDocumentEntity:
    filename: str
    char_count: int
    summary: str
    uploaded_at: datetime

    def __post_init__(self) -> None:
        if not self.filename.strip():
            raise ValueError("filename은 비어 있을 수 없습니다.")
        if not self.summary.strip():
            raise ValueError("summary는 비어 있을 수 없습니다.")
