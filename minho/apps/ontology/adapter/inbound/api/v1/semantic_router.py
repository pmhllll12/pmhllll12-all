from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from ontology.adapter.inbound.api.schema.semantic_chat_schemas import (
    SemanticChatRequest,
    SemanticChatResponse,
)
from ontology.app.dtos.semantic_chat_dto import SendSemanticChatCommand
from ontology.app.ports.input.semantic_chat_use_case import SemanticChatUseCase
from ontology.dependencies.semantic_chat_provider import get_semantic_chat_use_case

from core.matrix.vault_keymaker_secret_manager import MissingApiKeyError, format_gemini_error

semantic_chat_router = APIRouter(prefix="/semantic-chat", tags=["semantic-chat"])


@semantic_chat_router.post(
    "", response_model=SemanticChatResponse, summary="시멘틱 의도 판정 후 LangChain 챗봇 응답"
)
async def send_semantic_chat_message(
    body: SemanticChatRequest,
    use_case: SemanticChatUseCase = Depends(get_semantic_chat_use_case),
) -> SemanticChatResponse:
    message = body.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="message는 비어 있을 수 없습니다.")

    try:
        result = await use_case.handle_message(SendSemanticChatCommand(message=message))
    except MissingApiKeyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        status, detail = format_gemini_error(exc)
        raise HTTPException(status_code=status, detail=detail) from exc

    if not result.reply.strip():
        raise HTTPException(status_code=502, detail="모델이 비어 있는 응답을 반환했습니다.")

    return SemanticChatResponse(
        reply=result.reply,
        model=result.model,
        intent_label=result.intent_label,
        intent_confidence=result.intent_confidence,
    )
