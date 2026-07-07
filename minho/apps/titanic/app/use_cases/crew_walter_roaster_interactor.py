from __future__ import annotations

from titanic.adapter.inbound.api.schemas.crew_walter_roaster_schemas import WalterRoasterSchema
from titanic.app.dtos.crew_walter_roaster_dto import WalterRoasterQuery, WalterRoasterResponse
from titanic.app.ports.input.crew_walter_roaster_use_case import WalterRoasterUseCase
from titanic.app.ports.output.crew_walter_roaster_port import WalterRoasterPort


class WalterRoasterInteractor(WalterRoasterUseCase):
    def __init__(self, repository: WalterRoasterPort) -> None:
        self.repository = repository

    async def get_train_set(self) -> pd.DataFrame:
        '''월터가 DB에서 train set만 가져오는 메소드'''
        return await self.repository.get_train_set()

    async def get_test_set(self) -> pd.DataFrame:
        '''월터가 DB에서 test set만 가져오는 메소드'''
        return await self.repository.get_test_set()

    def introduce_myself(self, schema: WalterRoasterSchema) -> WalterRoasterResponse:
        query = WalterRoasterQuery(id=schema.id, name=schema.name, memo=schema.memo)
        return self.repository.introduce_myself(query)
