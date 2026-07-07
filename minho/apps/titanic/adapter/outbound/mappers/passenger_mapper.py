from __future__ import annotations

from titanic.adapter.outbound.orm.passenger_orm import PersonOrm
from titanic.domain.entities.crew_james_director_entity import JamesPersonEntity


def james_person_entity_from_orm(orm: PersonOrm) -> JamesPersonEntity:
    return JamesPersonEntity(
        id=orm.id,
        passenger_id=orm.passenger_id,
        name=orm.name,
        gender=orm.gender,
        age=orm.age,
        sib_sp=orm.sib_sp,
        parch=orm.parch,
        survived=orm.survived,
    )


def james_person_orm_from_entity(entity: JamesPersonEntity) -> PersonOrm:
    kw: dict = {
        "passenger_id": entity.passenger_id,
        "name": entity.name,
        "gender": entity.gender,
        "age": entity.age,
        "sib_sp": entity.sib_sp,
        "parch": entity.parch,
        "survived": entity.survived,
    }
    if entity.id is not None:
        kw["id"] = entity.id
    return PersonOrm(**kw)


__all__ = ["james_person_entity_from_orm", "james_person_orm_from_entity"]
