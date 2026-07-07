from __future__ import annotations

from abc import ABC, abstractmethod

from community.app.dtos.receiver_dto import (
    ReceivedEmailLog,
    ReceiveEmailCommand,
    ReceiveEmailResult,
)


class ReceiverUseCase(ABC):
    @abstractmethod
    async def receive(self, command: ReceiveEmailCommand) -> ReceiveEmailResult:
        raise NotImplementedError

    @abstractmethod
    async def get_logs(self) -> list[ReceivedEmailLog]:
        raise NotImplementedError
