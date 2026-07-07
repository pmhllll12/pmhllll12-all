from __future__ import annotations

from community.adapter.inbound.api.schemas.community_host_schemas import (
    CommunityHostResponse,
    CommunityHostSchema,
)
from community.app.dtos.community_host_dto import CommunityHostQuery
from community.app.ports.input.community_host_use_case import CommunityHostUseCase
from community.domain.community_host import CommunityHost


class CommunityHostInteractor(CommunityHostUseCase):
    async def introduce_myself(self, schema: CommunityHostSchema) -> CommunityHostResponse:
        query = CommunityHostQuery(id=schema.id, name=schema.name)
        host = CommunityHost.default()
        return CommunityHostResponse(
            id=query.id,
            name=host.name,
            role=host.role,
            channels=list(host.channels),
            greeting=host.greeting,
        )
