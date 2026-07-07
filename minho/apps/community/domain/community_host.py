from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CommunityHost:
    id: int
    name: str
    role: str
    channels: tuple[str, ...]
    greeting: str

    @classmethod
    def default(cls) -> "CommunityHost":
        return cls(
            id=1,
            name="커뮤니티 호스트",
            role="소통 채널 관리자",
            channels=("이메일", "주소록", "디스코드", "텔레그램"),
            greeting="안녕하세요! 저는 커뮤니티의 소통 채널을 담당하는 호스트입니다.",
        )
