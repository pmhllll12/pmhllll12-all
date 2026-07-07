from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WatcherEvent:
    """왓슨(Watson)이 인터셉트하는 인바운드 이벤트 — 채널(텔레그램/디스코드 등) 무관 공통 형태."""

    channel: str
    sender: str
    content: str
    important_client: bool

    def __post_init__(self) -> None:
        if not self.channel.strip():
            raise ValueError("channel은 비어 있을 수 없습니다.")
        if not self.content.strip():
            raise ValueError("content는 비어 있을 수 없습니다.")
