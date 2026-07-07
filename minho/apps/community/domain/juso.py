from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Juso:
    id: int
    name: str
    role: str
    responsibilities: tuple[str, ...]
    greeting: str

    @classmethod
    def default(cls) -> "Juso":
        return cls(
            id=2,
            name="주소록 관리자",
            role="연락처 및 주소 관리 담당",
            responsibilities=("CSV 업로드", "연락처 등록", "닉네임 검색", "이메일 연동"),
            greeting="안녕하세요! 저는 커뮤니티 주소록을 관리하는 담당자입니다.",
        )
