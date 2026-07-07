from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EmbarkedType(str, Enum):
    CHERBOURG = "C"
    QUEENSTOWN = "Q"
    SOUTHAMPTON = "S"


@dataclass(frozen=True)
class Embarked:
    value: EmbarkedType

    @classmethod
    def from_raw(cls, raw: str | None) -> Embarked:
        if raw is None or raw.strip() == "":
            raise ValueError("Embarked는 필수 값입니다.")
        try:
            return cls(value=EmbarkedType(raw.strip().upper()))
        except ValueError:
            raise ValueError(f"Embarked 유효하지 않은 값: '{raw}'")

    def __str__(self) -> str:
        return self.value.value
