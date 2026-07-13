from __future__ import annotations

from abc import ABC, abstractmethod

from admin.adapter.inbound.schema.piper_dinesh_dash_schema import DineshDashSchema
from admin.app.dtos.piper_dinesh_dash_dto import DineshDashResponse


class DineshDashUseCase(ABC):

    @abstractmethod
    def introduce_myself(self, schema: DineshDashSchema) -> DineshDashResponse:
        '''디네시 추그타이의 자기소개 메소드'''
        pass
