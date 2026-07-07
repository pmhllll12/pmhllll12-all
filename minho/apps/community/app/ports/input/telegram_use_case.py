from __future__ import annotations

from abc import ABC, abstractmethod

from community.adapter.inbound.api.schemas.telegram_schemas import TelegramResponse, TelegramSchema


class TelegramUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: TelegramSchema) -> TelegramResponse:
        raise NotImplementedError
