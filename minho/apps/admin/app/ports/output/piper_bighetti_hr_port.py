from __future__ import annotations

from abc import ABC, abstractmethod

from admin.app.dtos.piper_bighetti_hr_dto import BighettiHrQuery, BighettiHrResponse


class BighettiHrPort(ABC):
    @abstractmethod
    async def introduce_myself(self, query: BighettiHrQuery) -> BighettiHrResponse:
        """넬슨 '빅헤드' 비게티 레포지토리 추상 메소드"""
        raise NotImplementedError
