from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RoseModelEntity:
    """로즈 모델 예약/티켓 행 — `RoseModelOrm` 과 1:1 대응."""

    id: int | None
    person_id: int | None
    pclass: str | None
    ticket: str | None
    fare: str | None
    cabin: str | None
    embarked: str | None
