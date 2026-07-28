from __future__ import annotations

import asyncio
import logging
from typing import Any

from ontology.app.ports.output.chatbot_engine_port import ChatbotEnginePort
from ontology.domain.chat_intent import ChatIntent

from core.matrix.vault_keymaker_secret_manager import keymaker

logger = logging.getLogger(__name__)

_PROMPT_TEMPLATE = (
    "당신은 친절하고 간결하게 답하는 어시스턴트입니다. "
    "사용자 메시지의 의도는 '{intent_label}'로 판정되었습니다 — 이를 참고해 답하세요.\n\n"
    "{message}"
)


class GeminiChatbotEngine(ChatbotEnginePort):
    """Gemini로, 판정된 의도를 참고해 답하는 챗봇 엔진."""

    async def generate_reply(self, message: str, intent: ChatIntent) -> tuple[str, str]:
        prompt = _PROMPT_TEMPLATE.format(intent_label=intent.label, message=message)
        response, model_used = await asyncio.to_thread(keymaker.generate_content, prompt)
        reply = _extract_text(response)
        logger.info("[GeminiChatbotEngine] model=%s reply_len=%d", model_used, len(reply))
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
