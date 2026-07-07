from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from community.adapter.inbound.api.schemas.email_incoming_schemas import (
    EmailIncomingLogEntry,
    EmailIncomingRequest,
    EmailIncomingResponse,
)
from community.app.dtos.receiver_dto import ReceiveEmailCommand
from community.app.ports.input.receiver_use_case import ReceiverUseCase
from community.dependencies.receiver_provider import get_receiver_use_case
from core.matrix.vault_keymaker_secret_manager import MissingApiKeyError

receiver_router = APIRouter(prefix="/receiver", tags=["community-receiver"])


@receiver_router.post("/incoming", response_model=EmailIncomingResponse)
async def receive_incoming_email(
    body: EmailIncomingRequest,
    use_case: ReceiverUseCase = Depends(get_receiver_use_case),
) -> EmailIncomingResponse:
    """n8n Gmail Trigger가 새로 도착한 메일을 수신해 임베딩과 함께 pgvector에 저장합니다."""
    try:
        result = await use_case.receive(
            ReceiveEmailCommand(
                subject=body.subject,
                from_=body.from_,
                to=body.to,
                body=body.body,
                message_id=body.message_id,
            )
        )
    except MissingApiKeyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return EmailIncomingResponse(ok=result.ok, message=result.message)


@receiver_router.get("/logs", response_model=list[EmailIncomingLogEntry])
async def get_received_logs(
    use_case: ReceiverUseCase = Depends(get_receiver_use_case),
) -> list[EmailIncomingLogEntry]:
    """pgvector에 저장된 수신 메일 로그를 최신순으로 반환합니다 (최대 100건)."""
    logs = await use_case.get_logs()
    return [
        EmailIncomingLogEntry(
            received_at=log.received_at,
            subject=log.subject,
            from_=log.from_,
            to=log.to,
            body=log.body,
            message_id=log.message_id,
        )
        for log in logs
    ]
