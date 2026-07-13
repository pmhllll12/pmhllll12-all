from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DetectFacesCommand:
    image_path: str
    confidence: float = 0.25


@dataclass(frozen=True)
class FaceBoundingBox:
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float


@dataclass(frozen=True)
class DetectFacesResult:
    ok: bool
    boxes: list[FaceBoundingBox] = field(default_factory=list)
    message: str = "detected"
