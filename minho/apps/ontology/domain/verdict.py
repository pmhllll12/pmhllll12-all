from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Verdict:
    """Judge의 판정 결과. 스포크가 자기 도메인에 맞게 해석한다."""

    label: str
    confidence: float
    reason: str

    @property
    def is_spam(self) -> bool:
        return self.label.upper() == "SPAM"
