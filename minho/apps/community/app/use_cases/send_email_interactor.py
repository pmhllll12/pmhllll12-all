from __future__ import annotations

import logging

from community.app.dtos.send_email_dto import SendEmailCommand, SendEmailResult
from community.app.ports.input.send_email_use_case import SendEmailUseCase
from community.app.ports.output.email_client_port import EmailClientPort
from community.domain.email_message import EmailMessage

logger = logging.getLogger(__name__)


class SendEmailInteractor(SendEmailUseCase):
    def __init__(self, client: EmailClientPort) -> None:
        self._client = client

    async def send(self, command: SendEmailCommand) -> SendEmailResult:
        msg = EmailMessage(to_email=command.to_email, topic=command.topic)
        ok = await self._client.deliver(to_email=msg.to_email, topic=msg.topic)
        logger.info("[SendEmailInteractor] to=%s ok=%s", msg.to_email, ok)
        msg_text = f"{msg.to_email} 으로 발송 요청 완료" if ok else "n8n 발송 실패"
        return SendEmailResult(ok=ok, message=msg_text)
