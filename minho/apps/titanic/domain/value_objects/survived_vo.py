from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SurvivedType(int, Enum):
    DIED = 0
    SURVIVED = 1


@dataclass(frozen=True)
class SurvivedStatus:
    value: SurvivedType

    @classmethod
    def from_raw(cls, raw: str | None) -> SurvivedStatus:
        if raw is None or raw.strip() == "":
            raise ValueError("SurvivedStatus는 필수 값입니다.")
        try:
            return cls(value=SurvivedType(int(raw.strip())))
        except (ValueError, KeyError):
            raise ValueError(f"SurvivedStatus 유효하지 않은 값: '{raw}'")

    @property
    def is_survived(self) -> bool:
        return self.value == SurvivedType.SURVIVED

    def __str__(self) -> str:
        return str(self.value.value)
