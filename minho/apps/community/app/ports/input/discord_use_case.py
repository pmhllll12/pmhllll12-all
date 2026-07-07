from __future__ import annotations

from abc import ABC, abstractmethod

from community.adapter.inbound.api.schemas.discord_schemas import DiscordResponse, DiscordSchema


class DiscordUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: DiscordSchema) -> DiscordResponse:
        raise NotImplementedError
