from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Evidence:
    """스포크가 Judge에게 전달하는 추상 신호. 도메인 개념 없음."""

    source_app: str
    signals: dict[str, str]
