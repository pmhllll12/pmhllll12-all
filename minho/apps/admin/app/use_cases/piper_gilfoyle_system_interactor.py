from __future__ import annotations

from admin.adapter.inbound.schema.piper_gilfoyle_system_schema import GilfoyleSystemSchema
from admin.app.dtos.piper_gilfoyle_system_dto import (
    GilfoyleSystemQuery,
    GilfoyleSystemResponse,
)
from admin.app.ports.input.piper_gilfoyle_system_use_case import GilfoyleSystemUseCase
from admin.app.ports.output.piper_gilfoyle_system_port import GilfoyleSystemPort


class GilfoyleSystemInteractor(GilfoyleSystemUseCase):
    def __init__(self, repository: GilfoyleSystemPort) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: GilfoyleSystemSchema) -> GilfoyleSystemResponse:
        query = GilfoyleSystemQuery(
            route=schema.route,
            english_name=schema.english_name,
            korean_name=schema.korean_name,
        )
        return await self.repository.introduce_myself(query)
