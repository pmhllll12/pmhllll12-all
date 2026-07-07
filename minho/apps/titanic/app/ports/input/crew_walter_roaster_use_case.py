from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd
from titanic.adapter.inbound.api.schemas.crew_walter_roaster_schemas import WalterRoasterSchema
from titanic.app.dtos.crew_walter_roaster_dto import WalterRoasterResponse


class WalterRoasterUseCase(ABC):

    @abstractmethod
    async def get_train_set(self) -> pd.DataFrame:
        '''월터가 DB에서 훈련 데이터셋을 가져오는 메소드'''
        pass

    @abstractmethod
    async def get_test_set(self) -> pd.DataFrame:
        '''월터가 DB에서 테스트 데이터셋을 가져오는 메소드'''
        pass

    @abstractmethod
    def introduce_myself(self, schema: WalterRoasterSchema) -> WalterRoasterResponse:
        '''월터의 자기소개 메소드'''
        pass
