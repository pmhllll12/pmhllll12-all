from __future__ import annotations

import asyncio
import logging
from typing import Any

from admin.app.ports.output.receipt_ocr_port import ReceiptOcrPort

from core.matrix.vault_keymaker_secret_manager import keymaker

logger = logging.getLogger(__name__)

_PROMPT = (
    "이 영수증 이미지에 보이는 모든 텍스트를 그대로 옮겨 적으세요. "
    "줄바꿈은 원본 그대로 유지하고, 설명·요약·마크다운 서식을 덧붙이지 마세요."
)


class GeminiReceiptOcrClient(ReceiptOcrPort):
    """Gemini 멀티모달로 영수증 이미지의 텍스트를 그대로 추출한다."""

    async def extract_text(self, content: bytes, mime_type: str) -> str:
        response, model_used = await asyncio.to_thread(
            keymaker.generate_vision_content, _PROMPT, content, mime_type
        )
        text = _extract_text(response)
        logger.info("[GeminiReceiptOcrClient] model=%s text_len=%d", model_used, len(text))
        return text


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
