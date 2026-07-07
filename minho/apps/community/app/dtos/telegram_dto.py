from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TelegramQuery:
    id: int
    name: str


@dataclass(frozen=True)
class TelegramResult:
    id: int
    name: str
    role: str
    channels: tuple[str, ...]
    greeting: str
