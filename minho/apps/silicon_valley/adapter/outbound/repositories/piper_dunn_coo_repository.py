from __future__ import annotations

import logging

from silicon_valley.app.dtos.piper_dunn_coo_dto import DunnCooQuery, DunnCooResponse
from silicon_valley.app.ports.output.piper_dunn_coo_port import DunnCooPort
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class DunnCooRepository(DunnCooPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: DunnCooQuery) -> DunnCooResponse:
        logger.info("[DunnCooRepository] introduce_myself | request_data=%s", query)
        return DunnCooResponse(
            route=query.route,
            english_name=query.english_name,
            korean_name=query.korean_name,
        )
