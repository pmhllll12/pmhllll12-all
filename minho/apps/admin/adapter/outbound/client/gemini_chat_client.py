from __future__ import annotations

import asyncio
import logging
from typing import Any

from admin.app.ports.output.langchain_chat_client_port import LangchainChatClientPort

from core.matrix.vault_keymaker_secret_manager import keymaker

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = "당신은 친절하고 간결하게 답하는 어시스턴트입니다."


class GeminiChatClient(LangchainChatClientPort):
    """Gemini로 자유 대화를 처리한다."""

    async def generate_reply(self, message: str) -> tuple[str, str]:
        prompt = f"{_SYSTEM_PROMPT}\n\n{message}"
        response, model_used = await asyncio.to_thread(keymaker.generate_content, prompt)
        reply = _extract_text(response)
        logger.info("[GeminiChatClient] model=%s reply_len=%d", model_used, len(reply))
        return reply, model_used


def _extract_text(response: Any) -> str:
    try:
        text = (response.text or "").strip()
    except ValueError:
        text = ""
    if text:
        return text
    if response.candidates:
        parts = response.candidates[0].content.parts
        chunks = [getattr(p, "text", "") or "" for p in parts]
        return "".join(chunks).strip()
    return ""
