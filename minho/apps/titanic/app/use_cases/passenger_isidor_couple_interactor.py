from __future__ import annotations

from titanic.adapter.inbound.api.schemas.passenger_isidor_couple_schemas import IsidorBedSchema
from titanic.app.dtos.passenger_isidor_couple_dto import IsidorCoupleQuery, IsidorCoupleResponse
from titanic.app.ports.input.passenger_isidor_couple_use_case import IsidorCoupleUseCase
from titanic.app.ports.output.passenger_isidor_couple_port import IsidorCouplePort


class IsidorCoupleInteractor(IsidorCoupleUseCase):
    def __init__(self, repository: IsidorCouplePort) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: IsidorBedSchema) -> IsidorCoupleResponse:
        query = IsidorCoupleQuery(id=schema.id, name=schema.name)
        return await self.repository.introduce_myself(query)
