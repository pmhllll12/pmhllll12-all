from __future__ import annotations

from titanic.adapter.outbound.orm.booking_orm import BookingOrm
from titanic.domain.entities.crew_james_director_entity import JamesBookingEntity


def james_booking_entity_from_orm(orm: BookingOrm) -> JamesBookingEntity:
    return JamesBookingEntity(
        id=orm.id,
        person_id=orm.person_id,
        pclass=orm.pclass,
        ticket=orm.ticket,
        fare=orm.fare,
        cabin=orm.cabin,
        embarked=orm.embarked,
    )


def james_booking_orm_from_entity(entity: JamesBookingEntity) -> BookingOrm:
    if entity.person_id is None:
        raise ValueError("JamesBookingEntity.person_id is required to persist BookingOrm")
    kw: dict = {
        "person_id": entity.person_id,
        "pclass": entity.pclass,
        "ticket": entity.ticket,
        "fare": entity.fare,
        "cabin": entity.cabin,
        "embarked": entity.embarked,
    }
    if entity.id is not None:
        kw["id"] = entity.id
    return BookingOrm(**kw)


__all__ = ["james_booking_entity_from_orm", "james_booking_orm_from_entity"]
