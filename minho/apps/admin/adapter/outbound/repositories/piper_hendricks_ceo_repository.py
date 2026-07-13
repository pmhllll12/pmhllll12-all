from __future__ import annotations

import logging

from admin.app.dtos.piper_hendricks_ceo_dto import HendricksCeoQuery, HendricksCeoResponse
from admin.app.ports.output.piper_hendricks_ceo_port import HendricksCeoPort
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class HendricksCeoRepository(HendricksCeoPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: HendricksCeoQuery) -> HendricksCeoResponse:
        logger.info("[HendricksCeoRepository] introduce_myself | request_data=%s", query)
        return HendricksCeoResponse(
            route=query.route,
            english_name=query.english_name,
            korean_name=query.korean_name,
        )
