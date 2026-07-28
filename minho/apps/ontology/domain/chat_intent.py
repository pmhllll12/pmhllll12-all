from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChatIntent:
    """자유 대화 메시지의 시멘틱 의도 판정 결과."""

    label: str
    confidence: float
    reason: str
