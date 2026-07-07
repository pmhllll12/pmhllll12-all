from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EmailMessage:
    to_email: str
    topic: str

    def __post_init__(self) -> None:
        if not self.to_email or "@" not in self.to_email:
            raise ValueError(f"유효하지 않은 이메일: {self.to_email!r}")
        if not self.topic.strip():
            raise ValueError("topic은 비어 있을 수 없습니다.")
