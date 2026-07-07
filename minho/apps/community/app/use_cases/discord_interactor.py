from __future__ import annotations

from community.adapter.inbound.api.schemas.discord_schemas import DiscordResponse, DiscordSchema
from community.app.dtos.discord_dto import DiscordQuery
from community.app.ports.input.discord_use_case import DiscordUseCase
from community.domain.discord_host import DiscordHost


class DiscordInteractor(DiscordUseCase):
    async def introduce_myself(self, schema: DiscordSchema) -> DiscordResponse:
        query = DiscordQuery(id=schema.id, name=schema.name)
        host = DiscordHost.default()
        return DiscordResponse(
            id=query.id,
            name=host.name,
            role=host.role,
            channels=list(host.channels),
            greeting=host.greeting,
        )
