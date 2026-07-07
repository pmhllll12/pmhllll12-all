from __future__ import annotations

from abc import ABC, abstractmethod

from community.adapter.inbound.api.schemas.watcher_schemas import WatcherHostResponse, WatcherSchema
from community.app.dtos.watcher_dto import (
    WatcherJourneyLog,
    WatchEventCommand,
    WatchEventResult,
)


class WatcherUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: WatcherSchema) -> WatcherHostResponse:
        raise NotImplementedError

    @abstractmethod
    async def watch(self, command: WatchEventCommand) -> WatchEventResult:
        raise NotImplementedError

    @abstractmethod
    async def get_logs(self) -> list[WatcherJourneyLog]:
        raise NotImplementedError
