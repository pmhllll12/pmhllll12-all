from __future__ import annotations

import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ontology.app.dtos.vision_dto import StoredImage
from ontology.app.ports.output.vision_port import VisionPort

logger = logging.getLogger(__name__)


class VisionRepository(VisionPort):
    """분석된 이미지 결과를 pgvector(`vision_analyzed_images`)에 저장합니다."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(
        self,
        filename: str,
        caption: str,
        tags: list[str],
        image_key: str,
        analyzed_at: datetime,
    ) -> None:
        from ontology.adapter.outbound.orm.vision_orm import AnalyzedImageOrm

        row = AnalyzedImageOrm(
            filename=filename,
            caption=caption,
            tags=tags,
            image_key=image_key,
            analyzed_at=analyzed_at,
        )
        self.session.add(row)
        await self.session.commit()
        logger.info("[VisionRepository] save filename=%r id=%s", filename, row.id)

    async def list_recent(self, limit: int = 100) -> list[StoredImage]:
        from ontology.adapter.outbound.orm.vision_orm import AnalyzedImageOrm

        stmt = (
            select(AnalyzedImageOrm)
            .order_by(AnalyzedImageOrm.analyzed_at.desc())
            .limit(limit)
        )
        rows = (await self.session.execute(stmt)).scalars().all()
        return [
            StoredImage(
                analyzed_at=row.analyzed_at.isoformat(),
                filename=row.filename,
                caption=row.caption,
                tags=list(row.tags or []),
                image_key=row.image_key,
            )
            for row in rows
        ]
