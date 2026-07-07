from __future__ import annotations

from titanic.adapter.inbound.api.schemas.crew_james_director_schema import JamesDirectorSchema
from titanic.app.dtos.crew_james_director_dto import JamesDirectorQuery, JamesDirectorResponse
from titanic.app.ports.input.crew_james_director_use_case import JamesDirectorUseCase
from titanic.app.ports.output.crew_james_director_port import JamesDirectorPort


class JamesDirectorInteractor(JamesDirectorUseCase):
    def __init__(self, repository: JamesDirectorPort) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: JamesDirectorSchema) -> JamesDirectorResponse:
        query = JamesDirectorQuery(
            id=schema.id if schema.id is not None else 0,
            name=schema.name or "",
        )
        return await self.repository.introduce_myself(query)

    async def upload_titanic_file(self, schema: list[JamesDirectorSchema]) -> JamesDirectorResponse:
        return await self.repository.upload_titanic_file(schema)
