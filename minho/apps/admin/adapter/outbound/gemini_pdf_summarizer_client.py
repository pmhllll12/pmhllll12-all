from __future__ import annotations

import asyncio
import logging
from typing import Any

from admin.app.ports.output.pdf_summarizer_port import PdfSummarizerPort

from core.matrix.vault_keymaker_secret_manager import keymaker

logger = logging.getLogger(__name__)

# Gemini 컨텍스트 여유를 위한 추출 텍스트 상한(문자 수).
_MAX_CHARS_FOR_PROMPT = 20000

_PROMPT_TEMPLATE = (
    "다음은 업로드된 PDF 문서에서 추출한 텍스트입니다. 핵심 내용을 한국어로 "
    "5문장 이내로 요약하세요.\n\n{text}"
)


class GeminiPdfSummarizerClient(PdfSummarizerPort):
    """Gemini로 추출된 PDF 텍스트를 한국어로 요약한다."""

    async def summarize(self, text: str) -> str:
        prompt = _PROMPT_TEMPLATE.format(text=text[:_MAX_CHARS_FOR_PROMPT])
        response, model_used = await asyncio.to_thread(keymaker.generate_content, prompt)
        summary = _extract_text(response)
        logger.info("[GeminiPdfSummarizerClient] model=%s summary_len=%d", model_used, len(summary))
        return summary


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
