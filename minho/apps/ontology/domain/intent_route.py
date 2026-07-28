from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IntentRoute:
    """시멘틱 라우팅의 후보 의도 하나 — 예시 발화로 정의된다."""

    label: str
    example_utterances: list[str]

    def __post_init__(self) -> None:
        if not self.label.strip():
            raise ValueError("label은 비어 있을 수 없습니다.")
        if not self.example_utterances:
            raise ValueError("example_utterances는 최소 1개 이상이어야 합니다.")
