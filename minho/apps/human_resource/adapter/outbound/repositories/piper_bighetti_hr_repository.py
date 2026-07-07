from __future__ import annotations

import logging

from silicon_valley.app.dtos.piper_bighetti_hr_dto import BighettiHrQuery, BighettiHrResponse
from silicon_valley.app.ports.output.piper_bighetti_hr_port import BighettiHrPort
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class BighettiHrRepository(BighettiHrPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: BighettiHrQuery) -> BighettiHrResponse:
        logger.info("[BighettiHrRepository] introduce_myself | request_data=%s", query)
        return BighettiHrResponse(
            route=query.route,
            english_name=query.english_name,
            korean_name=query.korean_name,
        )
