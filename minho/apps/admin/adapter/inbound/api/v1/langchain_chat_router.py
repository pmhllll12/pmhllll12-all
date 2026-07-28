from __future__ import annotations

from admin.adapter.inbound.schema.langchain_chat_schema import (
    LangchainChatRequest,
    LangchainChatResponse,
)
from admin.app.dtos.langchain_chat_dto import SendChatMessageCommand
from admin.app.ports.input.langchain_chat_use_case import LangchainChatUseCase
from admin.dependencies.langchain_chat_provider import get_langchain_chat_use_case
from fastapi import APIRouter, Depends, HTTPException

from core.matrix.vault_keymaker_secret_manager import MissingApiKeyError, format_gemini_error

langchain_chat_router = APIRouter(prefix="/langchain-chat", tags=["langchain-chat"])


@langchain_chat_router.post("", response_model=LangchainChatResponse, summary="LangChain 자유 대화")
async def send_message(
    body: LangchainChatRequest,
    use_case: LangchainChatUseCase = Depends(get_langchain_chat_use_case),
) -> LangchainChatResponse:
    message = body.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="message는 비어 있을 수 없습니다.")

    try:
        result = await use_case.send_message(SendChatMessageCommand(message=message))
    except MissingApiKeyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        status, detail = format_gemini_error(exc)
        raise HTTPException(status_code=status, detail=detail) from exc

    if not result.reply.strip():
        raise HTTPException(status_code=502, detail="모델이 비어 있는 응답을 반환했습니다.")

    return LangchainChatResponse(reply=result.reply, model=result.model)
