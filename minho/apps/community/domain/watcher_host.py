from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WatcherHost:
    id: int
    name: str
    role: str
    features: tuple[str, ...]
    greeting: str

    @classmethod
    def default(cls) -> "WatcherHost":
        return cls(
            id=6,
            name="왓슨 (Watson)",
            role="인바운드 이벤트 초진(Triage) 및 라우팅 담당",
            features=(
                "Case A: 홈즈(Holmes) 자체 처리",
                "Case B: 스타크래프트 경유 페이커(Faker) 에스컬레이션",
                "라우팅 저니 추적 로그",
            ),
            greeting="안녕하세요! 저는 인바운드 이벤트를 초진해 라우팅하는 왓슨입니다.",
        )
