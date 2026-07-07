from __future__ import annotations

from abc import ABC, abstractmethod

from community.app.dtos.juso_dto import JusoContactRecord, JusoContactSuggestionResult


class JusoContactPort(ABC):
    @abstractmethod
    async def save_contacts(self, records: list[JusoContactRecord]) -> int:
        raise NotImplementedError

    @abstractmethod
    async def search_contacts(self, q: str, limit: int = 5) -> list[JusoContactSuggestionResult]:
        raise NotImplementedError
