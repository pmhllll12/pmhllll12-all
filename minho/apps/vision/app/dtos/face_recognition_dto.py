from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PredictFaceCommand:
    content: bytes
    filename: str
    mime_type: str


@dataclass(frozen=True)
class PredictFaceResult:
    ok: bool
    predicted_name: str
    confidence: float
    message: str = "predicted"
