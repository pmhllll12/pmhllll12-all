from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EmailHostQuery:
    id: int
    name: str


@dataclass(frozen=True)
class EmailHostResult:
    id: int
    name: str
    role: str
    features: tuple[str, ...]
    greeting: str
