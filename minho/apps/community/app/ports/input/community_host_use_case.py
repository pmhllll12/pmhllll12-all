from __future__ import annotations

from abc import ABC, abstractmethod

from community.adapter.inbound.api.schemas.community_host_schemas import (
    CommunityHostResponse,
    CommunityHostSchema,
)


class CommunityHostUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: CommunityHostSchema) -> CommunityHostResponse:
        raise NotImplementedError
