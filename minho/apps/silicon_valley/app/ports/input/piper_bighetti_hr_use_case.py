from __future__ import annotations

from abc import ABC, abstractmethod

from silicon_valley.adapter.inbound.schema.piper_bighetti_hr_schema import BighettiHrSchema
from silicon_valley.app.dtos.piper_bighetti_hr_dto import BighettiHrResponse


class BighettiHrUseCase(ABC):

    @abstractmethod
    def introduce_myself(self, schema: BighettiHrSchema) -> BighettiHrResponse:
        '''넬슨 '빅헤드' 비게티의 자기소개 메소드'''
        pass
