from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DiscordHost:
    id: int
    name: str
    role: str
    channels: tuple[str, ...]
    greeting: str

    @classmethod
    def default(cls) -> "DiscordHost":
        return cls(
            id=3,
            name="디스코드 관리자",
            role="디스코드 채널 운영 담당",
            channels=("공지", "자유대화", "질문답변", "프로젝트"),
            greeting="안녕하세요! 저는 커뮤니티 디스코드 채널을 운영하는 담당자입니다.",
        )
