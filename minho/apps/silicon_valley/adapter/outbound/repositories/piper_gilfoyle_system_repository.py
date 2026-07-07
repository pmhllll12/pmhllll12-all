from __future__ import annotations

import logging

from silicon_valley.app.dtos.piper_gilfoyle_system_dto import (
    GilfoyleSystemQuery,
    GilfoyleSystemResponse,
)
from silicon_valley.app.ports.output.piper_gilfoyle_system_port import GilfoyleSystemPort
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class GilfoyleSystemRepository(GilfoyleSystemPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: GilfoyleSystemQuery) -> GilfoyleSystemResponse:
        logger.info("[GilfoyleSystemRepository] introduce_myself | request_data=%s", query)
        return GilfoyleSystemResponse(
            route=query.route,
            english_name=query.english_name,
            korean_name=query.korean_name,
        )
