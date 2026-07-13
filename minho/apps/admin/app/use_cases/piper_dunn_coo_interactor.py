from __future__ import annotations

from admin.adapter.inbound.schema.piper_dunn_coo_schema import DunnCooSchema
from admin.app.dtos.piper_dunn_coo_dto import DunnCooQuery, DunnCooResponse
from admin.app.ports.input.piper_dunn_coo_use_case import DunnCooUseCase
from admin.app.ports.output.piper_dunn_coo_port import DunnCooPort


class DunnCooInteractor(DunnCooUseCase):
    def __init__(self, repository: DunnCooPort) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: DunnCooSchema) -> DunnCooResponse:
        query = DunnCooQuery(
            route=schema.route,
            english_name=schema.english_name,
            korean_name=schema.korean_name,
        )
        return await self.repository.introduce_myself(query)
