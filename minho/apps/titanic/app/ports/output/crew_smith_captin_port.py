from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.crew_smith_captin_dto import SmithCaptainQuery, SmithCaptainResponse


class SmithCaptainPort(ABC):
    @abstractmethod
    async def introduce_myself(self, query: SmithCaptainQuery) -> SmithCaptainResponse:
        raise NotImplementedError
