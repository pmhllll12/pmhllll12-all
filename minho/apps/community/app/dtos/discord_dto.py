from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DiscordQuery:
    id: int
    name: str


@dataclass(frozen=True)
class DiscordResult:
    id: int
    name: str
    role: str
    channels: tuple[str, ...]
    greeting: str
