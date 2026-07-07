from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.app.dtos.piper_dunn_coo_dto import DunnCooQuery, DunnCooResponse


class DunnCooPort(ABC):
    @abstractmethod
    async def introduce_myself(self, query: DunnCooQuery) -> DunnCooResponse:
        """자레드 던 레포지토리 추상 메소드"""
        raise NotImplementedError
