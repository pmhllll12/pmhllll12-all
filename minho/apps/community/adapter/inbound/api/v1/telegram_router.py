from __future__ import annotations

import asyncio
import logging
import os

import httpx
from fastapi import APIRouter, Depends, HTTPException

from community.adapter.inbound.api.schemas.telegram_schemas import (
    TelegramResponse,
    TelegramSchema,
    TelegramSendRequest,
    TelegramSendResponse,
)
from community.app.ports.input.telegram_use_case import TelegramUseCase
from community.dependencies.providers import get_telegram_use_case

telegram_router = APIRouter(prefix="/telegram", tags=["telegram"])
logger = logging.getLogger(__name__)


@telegram_router.get("/myself", response_model=TelegramResponse)
async def introduce_myself(
    use_case: TelegramUseCase = Depends(get_telegram_use_case),
) -> TelegramResponse:
    return await use_case.introduce_myself(
        TelegramSchema(id=4, name="텔레그램 관리자")
    )


@telegram_router.post("/send", response_model=TelegramSendResponse)
async def send_message(body: TelegramSendRequest) -> TelegramSendResponse:
    """Telegram Bot API로 메시지를 전송합니다."""
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    if not token:
        raise HTTPException(
            status_code=503,
            detail="TELEGRAM_BOT_TOKEN이 .env에 설정되지 않았습니다. @BotFather에서 토큰을 발급받아 설정하세요.",
        )

    # chat_id 미입력 시 DEVELOPER_CHAT_ID 사용
    target_chat_id = body.chat_id.strip() or os.getenv("DEVELOPER_CHAT_ID", "")
    if not target_chat_id:
        raise HTTPException(
            status_code=400,
            detail="채팅 ID를 입력하거나 .env에 DEVELOPER_CHAT_ID를 설정하세요.",
        )

    # 메시지 미입력 시 기본 메시지
    text = body.message.strip() or "안녕하세요! Minho Orchestrator에서 보내는 메시지입니다."

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": target_chat_id, "text": text}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
        data = resp.json()
        if not data.get("ok"):
            logger.warning("[telegram/send] API error: %s", data)
            raise HTTPException(status_code=400, detail=data.get("description", "Telegram API 오류"))
        logger.info("[telegram/send] chat_id=%s ok=True", target_chat_id)
        return TelegramSendResponse(ok=True, message=f"{target_chat_id} 으로 전송 완료")
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("[telegram/send] exception: %s", exc)
        raise HTTPException(status_code=502, detail=f"Telegram 전송 실패: {exc}") from exc
