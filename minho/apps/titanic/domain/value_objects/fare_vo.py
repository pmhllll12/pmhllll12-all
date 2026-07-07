from __future__ import annotations

from dataclasses import dataclass

_MIN_FARE = 0.0


@dataclass(frozen=True)
class Fare:
    value: float | None

    @classmethod
    def from_raw(cls, raw: str | None) -> Fare:
        if raw is None or raw.strip() == "":
            return cls(value=None)
        try:
            value = float(raw.strip())
        except ValueError:
            raise ValueError(f"Fare는 숫자여야 합니다: '{raw}'")
        if value < _MIN_FARE:
            raise ValueError(f"Fare는 {_MIN_FARE} 이상이어야 합니다: {value}")
        return cls(value=value)

    def per_person(self, family_size: int) -> float | None:
        if self.value is None or family_size <= 0:
            return None
        return self.value / family_size

    def __str__(self) -> str:
        return str(self.value) if self.value is not None else "Unknown"
