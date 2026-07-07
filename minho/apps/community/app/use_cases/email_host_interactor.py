from __future__ import annotations

from community.adapter.inbound.api.schemas.email_host_schemas import EmailHostResponse, EmailHostSchema
from community.app.dtos.email_host_dto import EmailHostQuery
from community.app.ports.input.email_host_use_case import EmailHostUseCase
from community.domain.email_host import EmailHost


class EmailHostInteractor(EmailHostUseCase):
    async def introduce_myself(self, schema: EmailHostSchema) -> EmailHostResponse:
        query = EmailHostQuery(id=schema.id, name=schema.name)
        host = EmailHost.default()
        return EmailHostResponse(
            id=query.id,
            name=host.name,
            role=host.role,
            features=list(host.features),
            greeting=host.greeting,
        )
