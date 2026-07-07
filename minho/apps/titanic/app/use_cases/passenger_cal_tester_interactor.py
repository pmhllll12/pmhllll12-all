from __future__ import annotations

import logging
from typing import Any

from titanic.adapter.inbound.api.schemas.passenger_cal_tester_schemas import CalTesterSchema
from titanic.app.dtos.passenger_cal_tester_dto import CalTesterQuery, CalTesterResponse
from titanic.app.ports.input.passenger_cal_tester_use_case import CalTesterUseCase
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.ports.output.passenger_cal_tester_port import CalTestPort

logger = logging.getLogger(__name__)


class CalTesterInteractor(CalTesterUseCase):
    def __init__(self, repository: CalTestPort, jack: JackTrainerUseCase) -> None:
        self.repository = repository
        self.jack = jack

    async def test_model(self, test_set) -> dict[str, Any]:
        """칼이 로즈가 제안한 10개 모델의 트레이닝 정도를 점수화 해서 1등을 뽑는것"""

        train_result = await self.jack.train_model(test_set)
        scores = train_result["scores"]

        ranking = []
        for name in scores:
            ranking.append({"model": name, "accuracy": scores[name]})
        ranking.sort(key=lambda entry: entry["accuracy"], reverse=True)

        rank = 1
        for entry in ranking:
            entry["rank"] = rank
            rank = rank + 1

        winner = ranking[0]["model"]
        logger.info("[CalTesterInteractor/test_model] ranking=%s winner=%s", ranking, winner)

        return {"ranking": ranking, "winner": winner}

    async def introduce_myself(self, schema: CalTesterSchema) -> CalTesterResponse:
        query = CalTesterQuery(id=schema.id, name=schema.name)
        return await self.repository.introduce_myself(query)
