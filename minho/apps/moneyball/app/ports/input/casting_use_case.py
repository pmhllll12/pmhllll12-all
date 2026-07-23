from __future__ import annotations

from abc import ABC, abstractmethod

from moneyball.app.dtos.casting_dto import CastingQuery, CastingResponse


class CastingUseCase(ABC):
    @abstractmethod
    async def cast(self, query: CastingQuery) -> CastingResponse:
        """포지션 기반으로 로스터를 포메이션 슬롯에 배치한다."""
        raise NotImplementedError


__all__ = ["CastingUseCase"]
