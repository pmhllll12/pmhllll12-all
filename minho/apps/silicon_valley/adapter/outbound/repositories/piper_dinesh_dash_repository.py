from __future__ import annotations

import logging

from silicon_valley.app.dtos.piper_dinesh_dash_dto import DineshDashQuery, DineshDashResponse
from silicon_valley.app.ports.output.piper_dinesh_dash_port import DineshDashPort
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class DineshDashRepository(DineshDashPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: DineshDashQuery) -> DineshDashResponse:
        logger.info("[DineshDashRepository] introduce_myself | request_data=%s", query)
        return DineshDashResponse(
            route=query.route,
            english_name=query.english_name,
            korean_name=query.korean_name,
        )
