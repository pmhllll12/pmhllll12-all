from __future__ import annotations

from dataclasses import dataclass


@dataclass
class JackTrainerEntity:
    """잭 트레이너 승객 행 — `JackTrainerOrm` 컬럼과 1:1 대응."""

    id: int | None
    passenger_id: str | None
    name: str | None
    gender: str | None
    age: str | None
    sib_sp: str | None
    parch: str | None
    survived: str | None
