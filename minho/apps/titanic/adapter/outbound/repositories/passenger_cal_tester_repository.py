from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession
from titanic.app.dtos.passenger_cal_tester_dto import CalTesterQuery, CalTesterResponse
from titanic.app.ports.output.passenger_cal_tester_port import CalTestPort

logger = logging.getLogger(__name__)


class CalTestRepository(CalTestPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: CalTesterQuery) -> CalTesterResponse:
        logger.info("[CalTestRepository] introduce_myself | request_data=%s", query)
        return CalTesterResponse(
            id=query.id * 10000,
            name=query.name + "가 레포지토리에 다녀옴",
        )
