from __future__ import annotations

from titanic.adapter.outbound.orm.crew_james_director_orm import JamesBookingOrm, JamesPersonOrm
from titanic.domain.entities.crew_james_director_entity import (
    JamesDirectorBookingEntity,
    JamesDirectorPersonEntity,
)


def james_director_person_entity_from_orm(orm: JamesPersonOrm) -> JamesDirectorPersonEntity:
    return JamesDirectorPersonEntity(
        passenger_id=orm.passenger_id,
        booking_id=orm.booking_id,
        embarked_code=orm.embarked_code,
        name=orm.name,
        gender=orm.gender,
        age=orm.age,
        sib_sp=orm.sib_sp,
        parch=orm.parch,
        survived=orm.survived,
    )


def james_director_person_orm_from_entity(entity: JamesDirectorPersonEntity) -> JamesPersonOrm:
    return JamesPersonOrm(
        passenger_id=entity.passenger_id,
        booking_id=entity.booking_id,
        embarked_code=entity.embarked_code,
        name=entity.name,
        gender=entity.gender,
        age=entity.age,
        sib_sp=entity.sib_sp,
        parch=entity.parch,
        survived=entity.survived,
    )


def james_director_booking_entity_from_orm(orm: JamesBookingOrm) -> JamesDirectorBookingEntity:
    return JamesDirectorBookingEntity(
        booking_id=orm.booking_id,
        pclass=orm.pclass,
        ticket=orm.ticket,
        fare=orm.fare,
        cabin=orm.cabin,
        embarked_code=orm.embarked_code,
        port_name=orm.port_name,
    )


def james_director_booking_orm_from_entity(entity: JamesDirectorBookingEntity) -> JamesBookingOrm:
    return JamesBookingOrm(
        booking_id=entity.booking_id,
        pclass=entity.pclass,
        ticket=entity.ticket,
        fare=entity.fare,
        cabin=entity.cabin,
        embarked_code=entity.embarked_code,
        port_name=entity.port_name,
    )


__all__ = [
    "james_director_person_entity_from_orm",
    "james_director_person_orm_from_entity",
    "james_director_booking_entity_from_orm",
    "james_director_booking_orm_from_entity",
]
