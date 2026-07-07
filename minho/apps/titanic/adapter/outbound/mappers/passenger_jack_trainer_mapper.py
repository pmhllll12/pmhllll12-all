from __future__ import annotations

from titanic.adapter.outbound.orm.passenger_jack_trainer_orm import JackTrainerOrm
from titanic.domain.entities.passenger_jack_trainer_entity import JackTrainerEntity


def jack_trainer_entity_from_orm(orm: JackTrainerOrm) -> JackTrainerEntity:
    return JackTrainerEntity(
        id=orm.id,
        passenger_id=orm.passenger_id,
        name=orm.name,
        gender=orm.gender,
        age=orm.age,
        sib_sp=orm.sib_sp,
        parch=orm.parch,
        survived=orm.survived,
    )


def jack_trainer_orm_from_entity(entity: JackTrainerEntity) -> JackTrainerOrm:
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
    return JackTrainerOrm(**kw)


__all__ = ["jack_trainer_entity_from_orm", "jack_trainer_orm_from_entity"]
