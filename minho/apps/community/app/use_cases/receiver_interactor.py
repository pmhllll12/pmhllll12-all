from __future__ import annotations

import logging
from datetime import datetime

from community.app.dtos.receiver_dto import (
    ReceivedEmailLog,
    ReceiveEmailCommand,
    ReceiveEmailResult,
)
from community.app.ports.input.receiver_use_case import ReceiverUseCase
from community.app.ports.output.content_filter_port import ContentFilterPort
from community.app.ports.output.embedding_port import EmbeddingPort
from community.app.ports.output.receiver_port import ReceiverPort
from community.domain.received_email import ReceivedEmail

logger = logging.getLogger(__name__)


class ReceiverInteractor(ReceiverUseCase):
    def __init__(
        self,
        repository: ReceiverPort,
        embedder: EmbeddingPort,
        content_filter: ContentFilterPort,
    ) -> None:
        self.repository = repository
        self.embedder = embedder
        self.content_filter = content_filter

    async def receive(self, command: ReceiveEmailCommand) -> ReceiveEmailResult:
        if command.message_id and await self.repository.exists_by_message_id(command.message_id):
            logger.info(
                "[ReceiverInteractor] duplicate skipped message_id=%r subject=%r",
                command.message_id,
                command.subject,
            )
            return ReceiveEmailResult(ok=True, message="이미 처리된 메일입니다 (중복 스킵).")

        if not await self.content_filter.is_normal(f"{command.subject}\n{command.body or ''}"):
            logger.info(
                "[ReceiverInteractor] blocked by content filter subject=%r from=%r",
                command.subject,
                command.from_,
            )
            return ReceiveEmailResult(
                ok=False, message="비정상 콘텐츠로 판정되어 저장이 차단되었습니다."
            )

        email = ReceivedEmail(
            subject=command.subject,
            from_=command.from_,
            to=command.to,
            body=command.body,
            received_at=datetime.now(),
            message_id=command.message_id,
        )
        embedding = await self.embedder.embed(f"{email.subject}\n{email.body or ''}")
        await self.repository.save(
            subject=email.subject,
            from_=email.from_,
            to=email.to,
            body=email.body,
            received_at=email.received_at,
            embedding=embedding,
            message_id=email.message_id,
        )
        logger.info("[ReceiverInteractor] receive subject=%r from=%r", email.subject, email.from_)
        return ReceiveEmailResult(ok=True, message="received")

    async def get_logs(self) -> list[ReceivedEmailLog]:
        return await self.repository.list_recent()
