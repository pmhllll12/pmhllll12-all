"""선수 임베딩 백필용 DTO — 임베딩 소스 텍스트와 실행 결과."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PlayerProfile:
    """`moneyball_players` 한 행에서 임베딩 소스로 쓰는 필드만 담는다."""

    player_id: str
    player_name: str | None = None
    e_player_name: str | None = None
    nickname: str | None = None
    position: str | None = None
    back_no: int | None = None
    nation: str | None = None
    height: int | None = None
    weight: int | None = None
    join_yyyy: str | None = None
    team_name: str | None = None

    def to_embedding_text(self) -> str:
        """임베딩에 넣을 한 문장. 이름이 전혀 없으면 빈 문자열(임베딩 대상 아님)."""
        name = _clean(self.player_name)
        e_name = _clean(self.e_player_name)
        if not name and not e_name:
            return ""

        if name and e_name:
            parts = [f"이름 {name} ({e_name})"]
        else:
            parts = [f"이름 {name or e_name}"]

        for label, value in (
            ("닉네임", _clean(self.nickname)),
            ("포지션", _clean(self.position)),
            ("등번호", self.back_no),
            ("국적", _clean(self.nation)),
            ("키", f"{self.height}cm" if self.height is not None else None),
            ("체중", f"{self.weight}kg" if self.weight is not None else None),
            ("입단", _clean(self.join_yyyy)),
            ("소속팀", _clean(self.team_name)),
        ):
            if value is not None:
                parts.append(f"{label} {value}")

        return ", ".join(parts)


@dataclass(frozen=True)
class BackfillCommand:
    """백필 1회 실행 파라미터."""

    limit: int | None = None
    batch_size: int = 20
    overwrite: bool = False
    sleep_seconds: float = 0.0
    dry_run: bool = False


@dataclass(frozen=True)
class BackfillResult:
    targeted: int = 0
    updated: int = 0
    skipped: int = 0
    failed: int = 0
    previews: list[str] = field(default_factory=list)


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


__all__ = ["BackfillCommand", "BackfillResult", "PlayerProfile"]
