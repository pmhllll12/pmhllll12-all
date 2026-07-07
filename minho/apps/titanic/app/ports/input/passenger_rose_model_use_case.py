from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from titanic.adapter.inbound.api.schemas.passenger_rose_model_schemas import RoseModelSchema
from titanic.app.dtos.passenger_rose_model_dto import RoseModelResponse


class RoseModelStrategy(ABC):
    """생존 예측 알고리즘 전략 인터페이스 (Strategy).

    `_docs/titanic-algorithm.md` TOP 10 알고리즘을 각각 구현체로 둔다.
    """

    name: str

    @abstractmethod
    def fit(self, features: Any, target: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def predict(self, features: Any) -> Any:
        raise NotImplementedError


class RoseModelUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: RoseModelSchema) -> RoseModelResponse:
        raise NotImplementedError
