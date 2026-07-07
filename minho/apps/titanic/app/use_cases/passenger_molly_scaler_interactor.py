from __future__ import annotations

from titanic.adapter.inbound.api.schemas.passenger_molly_scaler_schema import MollyScalerSchema
from titanic.app.dtos.passenger_molly_scaler_dto import MollyScalerQuery, MollyScalerResponse
from titanic.app.ports.input.passenger_molly_scaler_use_case import MollyScalerUseCase
from titanic.app.ports.output.passenger_molly_scaler_port import MollyScalerPort


class MollyScalerInteractor(MollyScalerUseCase):
    def __init__(self, repository: MollyScalerPort) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: MollyScalerSchema) -> MollyScalerResponse:
        query = MollyScalerQuery(id=schema.id, name=schema.name)
        return await self.repository.introduce_myself(query)
