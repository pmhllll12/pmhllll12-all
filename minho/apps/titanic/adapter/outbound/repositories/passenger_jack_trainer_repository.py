from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession
from titanic.app.dtos.passenger_jack_trainer_dto import JackTrainerQuery, JackTrainerResponse
from titanic.app.ports.output.passenger_jack_trainer_port import JackTrainerPort

logger = logging.getLogger(__name__)


class JackTrainRepository(JackTrainerPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: JackTrainerQuery) -> JackTrainerResponse:
        logger.info("[JackTrainRepository] introduce_myself | request_data=%s", query)
        return JackTrainerResponse(
            id=query.id * 10000,
            name=query.name + "가 레포지토리에 다녀옴",
        )
