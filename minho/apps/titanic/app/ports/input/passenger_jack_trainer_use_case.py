from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from titanic.adapter.inbound.api.schemas.passenger_jack_trainer_schemas import JackTrainerSchema
from titanic.app.dtos.passenger_jack_trainer_dto import JackTrainerResponse


class JackTrainerUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: JackTrainerSchema) -> JackTrainerResponse:
        """잭(트레이너) 자기소개."""
        raise NotImplementedError

    @abstractmethod
    async def train_model(self, train_set) -> dict[str, Any]:
        """로즈가 제안할 모델들을 훈련시키는 메소드"""

    @abstractmethod
    def predict_survival(self, profile: dict[str, Any]) -> dict[str, Any]:
        """학습된 모델 중 검증 정확도가 가장 높은 모델로 승객 프로필의 생존 여부를 예측"""
        