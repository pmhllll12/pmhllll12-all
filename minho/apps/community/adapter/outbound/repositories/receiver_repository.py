from __future__ import annotations

import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from community.app.dtos.receiver_dto import ReceivedEmailLog
from community.app.ports.output.receiver_port import ReceiverPort

logger = logging.getLogger(__name__)


class ReceiverRepository(ReceiverPort):
    """수신 메일 + 임베딩을 pgvector(`community_received_emails`)에 저장합니다."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def exists_by_message_id(self, message_id: str) -> bool:
        from community.adapter.outbound.orm.received_email_orm import ReceivedEmailOrm

        stmt = select(ReceivedEmailOrm.id).where(ReceivedEmailOrm.message_id == message_id).limit(1)
        row = (await self.session.execute(stmt)).first()
        return row is not None

    async def save(
        self,
        subject: str,
        from_: str | None,
        to: str | None,
        body: str | None,
        received_at: datetime,
        embedding: list[float],
        message_id: str | None = None,
    ) -> None:
        from community.adapter.outbound.orm.received_email_orm import ReceivedEmailOrm

        row = ReceivedEmailOrm(
            subject=subject,
            from_email=from_ or "",
            to_email=to or "",
            body=body or "",
            received_at=received_at,
            embedding=embedding,
            message_id=message_id,
        )
        self.session.add(row)
        await self.session.commit()
        logger.info("[ReceiverRepository] save subject=%r id=%s", subject, row.id)

    async def list_recent(self, limit: int = 100) -> list[ReceivedEmailLog]:
        from community.adapter.outbound.orm.received_email_orm import ReceivedEmailOrm

        stmt = (
            select(ReceivedEmailOrm)
            .order_by(ReceivedEmailOrm.received_at.desc())
            .limit(limit)
        )
        rows = (await self.session.execute(stmt)).scalars().all()
        return [
            ReceivedEmailLog(
                received_at=row.received_at.isoformat(),
                subject=row.subject,
                from_=row.from_email or None,
                to=row.to_email or None,
                body=row.body or None,
                message_id=row.message_id,
            )
            for row in rows
        ]
