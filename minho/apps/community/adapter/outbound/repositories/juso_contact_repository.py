from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from community.app.dtos.juso_dto import JusoContactRecord, JusoContactSuggestionResult
from community.app.ports.output.juso_contact_port import JusoContactPort

logger = logging.getLogger(__name__)


class JusoContactRepository(JusoContactPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_contacts(self, records: list[JusoContactRecord]) -> int:
        from community.adapter.outbound.orm.juso_contact_orm import JusoContactOrm
        from sqlalchemy.dialects.postgresql import insert as pg_insert

        if not records:
            return 0

        rows = [
            {
                "first_name": r.first_name,
                "middle_name": r.middle_name,
                "last_name": r.last_name,
                "nickname": r.nickname,
                "organization_name": r.organization_name,
                "organization_title": r.organization_title,
                "email_1_value": r.email_1_value,
                "phone_1_value": r.phone_1_value,
                "phone_2_value": r.phone_2_value,
                "address_1_city": r.address_1_city,
                "address_1_country": r.address_1_country,
                "birthday": r.birthday,
                "labels": r.labels,
            }
            for r in records
        ]

        await self.session.execute(pg_insert(JusoContactOrm).values(rows).on_conflict_do_nothing())
        await self.session.commit()

        logger.info("[JusoContactRepository] save_contacts saved=%d", len(rows))
        return len(rows)

    async def search_contacts(self, q: str, limit: int = 5) -> list[JusoContactSuggestionResult]:
        from community.adapter.outbound.orm.juso_contact_orm import JusoContactOrm
        from sqlalchemy import or_, select

        if not q:
            return []

        pattern = f"{q}%"
        stmt = (
            select(JusoContactOrm.nickname, JusoContactOrm.email_1_value)
            .where(
                or_(
                    JusoContactOrm.email_1_value.ilike(pattern),
                    JusoContactOrm.nickname.ilike(pattern),
                    JusoContactOrm.first_name.ilike(pattern),
                    JusoContactOrm.last_name.ilike(pattern),
                )
            )
            .where(JusoContactOrm.email_1_value != "")
            .limit(limit)
        )
        rows = (await self.session.execute(stmt)).all()
        logger.info("[JusoContactRepository] search_contacts q=%s found=%d", q, len(rows))
        return [
            JusoContactSuggestionResult(nickname=row.nickname or row.email_1_value, email=row.email_1_value)
            for row in rows
        ]
