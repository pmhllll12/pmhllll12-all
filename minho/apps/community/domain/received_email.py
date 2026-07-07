from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ReceivedEmail:
    subject: str
    from_: str | None
    to: str | None
    body: str | None
    received_at: datetime
    message_id: str | None = None

    def __post_init__(self) -> None:
        if not self.subject.strip():
            raise ValueError("subject는 비어 있을 수 없습니다.")
