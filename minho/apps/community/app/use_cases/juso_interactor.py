from __future__ import annotations

from community.adapter.inbound.api.schemas.juso_schemas import (
    JusoContactSchema,
    JusoContactSuggestion,
    JusoResponse,
    JusoSchema,
    JusoSearchResponse,
    JusoUploadResponse,
)
from community.app.dtos.juso_dto import JusoContactRecord, JusoQuery
from community.app.ports.input.juso_use_case import JusoUseCase
from community.app.ports.output.juso_contact_port import JusoContactPort
from community.domain.juso import Juso


class JusoInteractor(JusoUseCase):
    def __init__(self, repository: JusoContactPort) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: JusoSchema) -> JusoResponse:
        query = JusoQuery(id=schema.id, name=schema.name)
        juso = Juso.default()
        return JusoResponse(
            id=query.id,
            name=juso.name,
            role=juso.role,
            responsibilities=list(juso.responsibilities),
            greeting=juso.greeting,
        )

    async def upload_contacts(self, contacts: list[JusoContactSchema]) -> JusoUploadResponse:
        records = [
            JusoContactRecord(
                first_name=c.first_name,
                middle_name=c.middle_name,
                last_name=c.last_name,
                nickname=c.nickname,
                organization_name=c.organization_name,
                organization_title=c.organization_title,
                email_1_value=c.email_1_value,
                phone_1_value=c.phone_1_value,
                phone_2_value=c.phone_2_value,
                address_1_city=c.address_1_city,
                address_1_country=c.address_1_country,
                birthday=c.birthday,
                labels=c.labels,
            )
            for c in contacts
        ]
        count = await self.repository.save_contacts(records)
        return JusoUploadResponse(ok=True, count=count, message=f"{count}개의 연락처가 저장됐습니다.")

    async def search_contacts(self, q: str) -> JusoSearchResponse:
        suggestions = await self.repository.search_contacts(q.strip(), limit=5)
        return JusoSearchResponse(
            results=[JusoContactSuggestion(nickname=s.nickname, email=s.email) for s in suggestions]
        )
