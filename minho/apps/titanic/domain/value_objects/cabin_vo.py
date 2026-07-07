from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Cabin:
    value: str | None

    @classmethod
    def from_raw(cls, raw: str | None) -> Cabin:
        if raw is None or raw.strip() == "":
            return cls(value=None)
        return cls(value=raw.strip())

    @property
    def deck(self) -> str | None:
        return self.value[0] if self.value else None

    @property
    def has_cabin(self) -> bool:
        return self.value is not None

    def __str__(self) -> str:
        return self.value if self.value is not None else "Unknown"
