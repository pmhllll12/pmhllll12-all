from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ReceiptImageRef:
    """`receipts/` 폴더에 있는 이미지 한 건의 메타데이터. 아직 바이트는 없다."""

    key: str
    filename: str
    uploaded_at: datetime


@dataclass(frozen=True)
class ReceiptOcrResult:
    key: str
    filename: str
    uploaded_at: str
    ocr_text: str
