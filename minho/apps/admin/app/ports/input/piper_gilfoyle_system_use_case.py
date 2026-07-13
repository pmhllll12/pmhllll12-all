from __future__ import annotations

from abc import ABC, abstractmethod

from admin.adapter.inbound.schema.piper_gilfoyle_system_schema import GilfoyleSystemSchema
from admin.app.dtos.piper_gilfoyle_system_dto import GilfoyleSystemResponse


class GilfoyleSystemUseCase(ABC):

    @abstractmethod
    def introduce_myself(self, schema: GilfoyleSystemSchema) -> GilfoyleSystemResponse:
        '''버트럼 길포일의 자기소개 메소드'''
        pass
