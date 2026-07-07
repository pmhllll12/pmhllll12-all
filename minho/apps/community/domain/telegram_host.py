from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TelegramHost:
    id: int
    name: str
    role: str
    channels: tuple[str, ...]
    greeting: str

    @classmethod
    def default(cls) -> "TelegramHost":
        return cls(
            id=4,
            name="텔레그램 관리자",
            role="텔레그램 채널 운영 담당",
            channels=("공지 채널", "그룹 채팅", "봇 알림", "파일 공유"),
            greeting="안녕하세요! 저는 커뮤니티 텔레그램 채널을 운영하는 담당자입니다.",
        )
