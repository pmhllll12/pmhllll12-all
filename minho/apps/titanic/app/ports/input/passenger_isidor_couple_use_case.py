from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.adapter.inbound.api.schemas.passenger_isidor_couple_schemas import IsidorBedSchema
from titanic.app.dtos.passenger_isidor_couple_dto import IsidorCoupleResponse


class IsidorCoupleUseCase(ABC):

    @abstractmethod
    def introduce_myself(self, schema: IsidorBedSchema) -> IsidorCoupleResponse:
        '''이시도어 커플의 자기소개 메소드'''
        pass