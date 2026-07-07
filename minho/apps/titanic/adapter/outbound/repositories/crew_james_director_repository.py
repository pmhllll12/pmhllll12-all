from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession
from titanic.adapter.inbound.api.schemas.crew_james_director_schema import JamesDirectorSchema
from titanic.app.dtos.crew_james_director_dto import (
    BookingCommand,
    JamesDirectorQuery,
    JamesDirectorResponse,
    PassengerCommand,
)
from titanic.app.ports.output.crew_james_director_port import JamesDirectorPort

logger = logging.getLogger(__name__)


class JamesDirectorRepository(JamesDirectorPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: JamesDirectorQuery) -> JamesDirectorResponse:
        logger.info("[JamesDirectorRepository] introduce_myself | request_data=%s", query)
        return JamesDirectorResponse(id=query.id, name=query.name)

    async def upload_titanic_file(self, schema: list[JamesDirectorSchema]) -> JamesDirectorResponse:
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        from titanic.adapter.outbound.orm.passenger_jack_trainer_orm import JackTrainerOrm
        from titanic.adapter.outbound.orm.passenger_rose_model_orm import RoseModelOrm

        passenger_rows = [
            {
                "passenger_id": r.passenger_id,
                "name":         r.name         or "",
                "gender":       r.gender       or "",
                "age":          r.age          or "",
                "sib_sp":       r.sib_sp       or "0",
                "parch":        r.parch        or "0",
                "survived":     r.survived if r.survived not in (None, "") else None,
            }
            for r in schema if r.passenger_id
        ]

        if not passenger_rows:
            return JamesDirectorResponse(id=0, name="저장할 유효 행이 없습니다.")

        stmt = pg_insert(JackTrainerOrm).values(passenger_rows)
        stmt = stmt.on_conflict_do_update(
            index_elements=["passenger_id"],
            set_={c: stmt.excluded[c] for c in ("name", "gender", "age", "sib_sp", "parch", "survived")},
        )
        await self.session.execute(stmt)

        booking_rows = [
            {
                "passenger_id": r.passenger_id,
                "pclass":   r.pclass   or "",
                "ticket":   r.ticket   or "",
                "fare":     r.fare     or "",
                "cabin":    r.cabin    or "",
                "embarked": r.embarked or "",
            }
            for r in schema if r.passenger_id
        ]
        await self.session.execute(
            pg_insert(RoseModelOrm)
            .values(booking_rows)
            .on_conflict_do_nothing()
        )

        await self.session.commit()
        logger.info("[JamesDirectorRepository] upload_titanic_file saved=%d", len(passenger_rows))
        return JamesDirectorResponse(id=len(passenger_rows), name=f"CSV {len(passenger_rows)}행 저장 완료")

    async def receive_uploaded_records(
        self,
        person_commands: list[PassengerCommand],
        booking_commands: list[BookingCommand],
    ) -> int:
        from titanic.adapter.outbound.orm.booking_orm import BookingOrm
        from titanic.adapter.outbound.orm.passenger_orm import PersonOrm

        person_orms = [
            PersonOrm(
                passenger_id=cmd.passenger_id,
                name=cmd.name,
                gender=cmd.gender,
                age=cmd.age,
                sib_sp=cmd.sib_sp,
                parch=cmd.parch,
                survived=cmd.survived,
            )
            for cmd in person_commands
        ]
        self.session.add_all(person_orms)
        await self.session.flush()

        booking_orms = [
            BookingOrm(
                person_id=person_orm.id,
                pclass=cmd.pclass,
                ticket=cmd.ticket,
                fare=cmd.fare,
                cabin=cmd.cabin,
                embarked=cmd.embarked,
            )
            for person_orm, cmd in zip(person_orms, booking_commands, strict=False)
        ]
        self.session.add_all(booking_orms)
        await self.session.commit()

        return len(person_orms)
