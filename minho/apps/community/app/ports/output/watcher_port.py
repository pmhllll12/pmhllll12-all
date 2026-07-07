from __future__ import annotations

from abc import ABC, abstractmethod

from community.app.dtos.watcher_dto import WatcherJourneyLog


class WatcherPort(ABC):
    @abstractmethod
    async def save(self, log: WatcherJourneyLog) -> None:
        raise NotImplementedError

    @abstractmethod
    async def list_recent(self, limit: int = 100) -> list[WatcherJourneyLog]:
        raise NotImplementedError
