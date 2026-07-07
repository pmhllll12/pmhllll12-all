from __future__ import annotations

from abc import ABC, abstractmethod

from community.adapter.inbound.api.schemas.email_host_schemas import EmailHostResponse, EmailHostSchema


class EmailHostUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: EmailHostSchema) -> EmailHostResponse:
        raise NotImplementedError
