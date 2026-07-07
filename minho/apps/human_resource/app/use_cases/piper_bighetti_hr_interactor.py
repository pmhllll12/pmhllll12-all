from __future__ import annotations

from silicon_valley.adapter.inbound.schema.piper_bighetti_hr_schema import BighettiHrSchema
from silicon_valley.app.dtos.piper_bighetti_hr_dto import BighettiHrQuery, BighettiHrResponse
from silicon_valley.app.ports.input.piper_bighetti_hr_use_case import BighettiHrUseCase
from silicon_valley.app.ports.output.piper_bighetti_hr_port import BighettiHrPort


class BighettiHrInteractor(BighettiHrUseCase):
    def __init__(self, repository: BighettiHrPort) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: BighettiHrSchema) -> BighettiHrResponse:
        query = BighettiHrQuery(
            route=schema.route,
            english_name=schema.english_name,
            korean_name=schema.korean_name,
        )
        return await self.repository.introduce_myself(query)
