from __future__ import annotations

from titanic.adapter.outbound.orm.passenger_rose_model_orm import RoseModelOrm
from titanic.domain.entities.passenger_rose_model_entity import RoseModelEntity


def rose_model_entity_from_orm(orm: RoseModelOrm) -> RoseModelEntity:
    return RoseModelEntity(
        id=orm.id,
        person_id=orm.person_id,
        pclass=orm.pclass,
        ticket=orm.ticket,
        fare=orm.fare,
        cabin=orm.cabin,
        embarked=orm.embarked,
    )


def rose_model_orm_from_entity(entity: RoseModelEntity) -> RoseModelOrm:
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
    return RoseModelOrm(**kw)


__all__ = ["rose_model_entity_from_orm", "rose_model_orm_from_entity"]
