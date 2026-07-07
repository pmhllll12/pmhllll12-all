from __future__ import annotations

from community.adapter.inbound.api.schemas.telegram_schemas import TelegramResponse, TelegramSchema
from community.app.dtos.telegram_dto import TelegramQuery
from community.app.ports.input.telegram_use_case import TelegramUseCase
from community.domain.telegram_host import TelegramHost


class TelegramInteractor(TelegramUseCase):
    async def introduce_myself(self, schema: TelegramSchema) -> TelegramResponse:
        query = TelegramQuery(id=schema.id, name=schema.name)
        host = TelegramHost.default()
        return TelegramResponse(
            id=query.id,
            name=host.name,
            role=host.role,
            channels=list(host.channels),
            greeting=host.greeting,
        )
