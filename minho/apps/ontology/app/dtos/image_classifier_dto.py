from __future__ import annotations

from dataclasses import dataclass, field

# 0.5: 별도 라벨셋 캘리브레이션 없이 1000-class ImageNet top-1 softmax confidence를
# "믿을만함/애매함"으로 가르는 관습적 절반값. 도메인 특화 캘리브레이션 전까지의 기본값이다.
DEFAULT_CONFIDENCE_THRESHOLD = 0.5


@dataclass(frozen=True)
class ClassifyImageCommand:
    content: bytes
    filename: str = "unnamed"
    confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD


@dataclass(frozen=True)
class LabelScore:
    label: str
    confidence: float


@dataclass(frozen=True)
class ClassifyImageResult:
    ok: bool
    label: str
    confidence: float
    top5: list[LabelScore] = field(default_factory=list)
    uncertain: bool = False
    inference_ms: float = 0.0
    message: str = "classified"
