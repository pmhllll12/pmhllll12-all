from __future__ import annotations

from abc import ABC, abstractmethod

from admin.app.dtos.piper_dinesh_dash_dto import DineshDashQuery, DineshDashResponse


class DineshDashPort(ABC):
    @abstractmethod
    async def introduce_myself(self, query: DineshDashQuery) -> DineshDashResponse:
        """디네시 추그타이 레포지토리 추상 메소드"""
        raise NotImplementedError
