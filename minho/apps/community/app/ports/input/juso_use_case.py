from __future__ import annotations

from abc import ABC, abstractmethod

from community.adapter.inbound.api.schemas.juso_schemas import (
    JusoContactSchema,
    JusoResponse,
    JusoSchema,
    JusoSearchResponse,
    JusoUploadResponse,
)


class JusoUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: JusoSchema) -> JusoResponse:
        raise NotImplementedError

    @abstractmethod
    async def upload_contacts(self, contacts: list[JusoContactSchema]) -> JusoUploadResponse:
        raise NotImplementedError

    @abstractmethod
    async def search_contacts(self, q: str) -> JusoSearchResponse:
        raise NotImplementedError
