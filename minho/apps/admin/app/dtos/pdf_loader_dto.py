from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UploadPdfCommand:
    filename: str
    content: bytes


@dataclass(frozen=True)
class PdfSummaryResult:
    ok: bool
    filename: str
    char_count: int
    summary: str
    message: str = "summarized"


@dataclass(frozen=True)
class PdfSummaryLog:
    filename: str
    char_count: int
    summary: str
    uploaded_at: str
