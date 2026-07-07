from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EmailHost:
    id: int
    name: str
    role: str
    features: tuple[str, ...]
    greeting: str

    @classmethod
    def default(cls) -> "EmailHost":
        return cls(
            id=5,
            name="이메일 관리자",
            role="이메일 발송 및 스팸 판정 담당",
            features=("EXAONE 스팸 판정", "n8n 워크플로우 연동", "Gmail 자동 발송", "주소록 연동"),
            greeting="안녕하세요! 저는 커뮤니티 이메일 발송을 담당하는 관리자입니다.",
        )
