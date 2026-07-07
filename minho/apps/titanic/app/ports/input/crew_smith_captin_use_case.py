from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.adapter.inbound.api.schemas.crew_smith_captin_schemas import (
    SmithCaptainSchema,
    SmithChatRequest,
    SmithChatResponse,
)
from titanic.app.dtos.crew_smith_captin_dto import SmithCaptainResponse
from titanic.app.dtos.passenger_jack_trainer_dto import JackTrainerResponse
from titanic.app.dtos.passenger_rose_model_dto import RoseModelResponse


class SmithCaptainUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: SmithCaptainSchema) -> SmithCaptainResponse:
        """스미스 선장의 자기소개 메소드"""
        pass

    @abstractmethod
    async def chat(
        self,smith_schema: SmithCaptainSchema
    ) -> tuple[SmithCaptainResponse, JackTrainerResponse, RoseModelResponse]:
        """선장·잭·로즈 자기소개를 한 번에 실행합니다."""
        pass

    @abstractmethod
    async def chat(self, body: SmithChatRequest) -> SmithChatResponse:
        """사용자 자연어 입력을 받아 채팅 응답을 반환합니다."""
        pass
