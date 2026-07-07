from __future__ import annotations

from community.adapter.outbound.orm.juso_contact_orm import JusoContactOrm
from community.app.dtos.juso_dto import JusoContactRecord


class JusoContactMapper:
    @staticmethod
    def to_orm(record: JusoContactRecord) -> JusoContactOrm:
        return JusoContactOrm(
            first_name=record.first_name,
            middle_name=record.middle_name,
            last_name=record.last_name,
            nickname=record.nickname,
            organization_name=record.organization_name,
            organization_title=record.organization_title,
            email_1_value=record.email_1_value,
            phone_1_value=record.phone_1_value,
            phone_2_value=record.phone_2_value,
            address_1_city=record.address_1_city,
            address_1_country=record.address_1_country,
            birthday=record.birthday,
            labels=record.labels,
        )

    @staticmethod
    def from_orm(orm: JusoContactOrm) -> JusoContactRecord:
        return JusoContactRecord(
            first_name=orm.first_name,
            middle_name=orm.middle_name,
            last_name=orm.last_name,
            nickname=orm.nickname,
            organization_name=orm.organization_name,
            organization_title=orm.organization_title,
            email_1_value=orm.email_1_value,
            phone_1_value=orm.phone_1_value,
            phone_2_value=orm.phone_2_value,
            address_1_city=orm.address_1_city,
            address_1_country=orm.address_1_country,
            birthday=orm.birthday,
            labels=orm.labels,
        )
