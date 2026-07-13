from __future__ import annotations

from abc import ABC, abstractmethod

from admin.adapter.inbound.schema.piper_dunn_coo_schema import DunnCooSchema
from admin.app.dtos.piper_dunn_coo_dto import DunnCooResponse


class DunnCooUseCase(ABC):

    @abstractmethod
    def introduce_myself(self, schema: DunnCooSchema) -> DunnCooResponse:
        '''자레드 던의 자기소개 메소드'''
        pass
