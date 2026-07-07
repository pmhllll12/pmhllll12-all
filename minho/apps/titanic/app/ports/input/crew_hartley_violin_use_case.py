from __future__ import annotations

import io
from abc import ABC, abstractmethod

from pandas import DataFrame
from titanic.adapter.inbound.api.schemas.crew_hartley_violin_schemas import HartleyViolinSchema
from titanic.app.dtos.crew_hartley_violin_dto import HartleyViolinResponse


class HartleyViolinUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schema: HartleyViolinSchema) -> HartleyViolinResponse:
        '''하틀리 바이올린의 자기소개 메소드'''
        pass

    @abstractmethod
    def generate_correlation_plot(self, dataset: DataFrame) -> io.BytesIO:
        '''생존율 상관관계 히트맵을 PNG 이미지 버퍼로 생성'''
        pass

    @abstractmethod
    def get_survived_correlation_ranking(self, dataset: DataFrame) -> list[tuple[str, float]]:
        '''Survived와의 상관계수를 절댓값 내림차순으로 반환'''
        pass