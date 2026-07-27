from __future__ import annotations

import logging
from datetime import datetime

from admin.app.dtos.pdf_loader_dto import PdfSummaryLog
from admin.app.ports.output.pdf_loader_port import PdfLoaderPort
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class PdfLoaderRepository(PdfLoaderPort):
    """추출된 PDF 요약을 Postgres(`admin_pdf_summaries`)에 저장합니다."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(
        self,
        filename: str,
        char_count: int,
        summary: str,
        uploaded_at: datetime,
    ) -> None:
        from admin.adapter.outbound.orm.pdf_summary_orm import PdfSummaryOrm

        row = PdfSummaryOrm(
            filename=filename,
            char_count=char_count,
            summary=summary,
            uploaded_at=uploaded_at,
        )
        self.session.add(row)
        await self.session.commit()
        logger.info("[PdfLoaderRepository] save filename=%r id=%s", filename, row.id)

    async def list_recent(self, limit: int = 100) -> list[PdfSummaryLog]:
        from admin.adapter.outbound.orm.pdf_summary_orm import PdfSummaryOrm

        stmt = select(PdfSummaryOrm).order_by(PdfSummaryOrm.uploaded_at.desc()).limit(limit)
        rows = (await self.session.execute(stmt)).scalars().all()
        return [
            PdfSummaryLog(
                filename=row.filename,
                char_count=row.char_count,
                summary=row.summary,
                uploaded_at=row.uploaded_at.isoformat(),
            )
            for row in rows
        ]
