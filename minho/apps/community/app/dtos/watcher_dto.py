from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class WatchEventCommand:
    channel: str
    sender: str
    content: str
    important_client: bool = False


@dataclass(frozen=True)
class WatchEventResult:
    ok: bool
    route: str
    message: str


@dataclass(frozen=True)
class WatcherJourneyLog:
    received_at: str
    channel: str
    sender: str
    route: str
    steps: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class WatcherHostQuery:
    id: int
    name: str


@dataclass(frozen=True)
class WatcherHostResult:
    id: int
    name: str
    role: str
    features: tuple[str, ...]
    greeting: str
