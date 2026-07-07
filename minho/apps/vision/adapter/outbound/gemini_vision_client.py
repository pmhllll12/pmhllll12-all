from __future__ import annotations

import asyncio
import logging
import re
from typing import Any

from vision.app.ports.output.image_captioning_port import ImageCaptioningPort

from core.matrix.vault_keymaker_secret_manager import keymaker

logger = logging.getLogger(__name__)

_PROMPT = (
    "이 이미지를 한국어로 분석하세요.\n"
    "반드시 아래 두 줄 형식으로만 답하세요:\n"
    "CAPTION: <이미지에 대한 한 문장 설명>\n"
    "TAGS: <쉼표로 구분된 태그 3~7개, 명사 위주>"
)
_CAPTION_RE = re.compile(r"CAPTION\s*:\s*(.+)")
_TAGS_RE = re.compile(r"TAGS\s*:\s*(.+)")


class GeminiVisionClient(ImageCaptioningPort):
    """Gemini 멀티모달로 이미지 설명(caption)과 태그를 생성한다."""

    async def caption(self, content: bytes, mime_type: str) -> tuple[str, list[str]]:
        response, model_used = await asyncio.to_thread(
            keymaker.generate_vision_content, _PROMPT, content, mime_type
        )
        text = _extract_text(response)

        caption_match = _CAPTION_RE.search(text)
        tags_match = _TAGS_RE.search(text)
        caption = caption_match.group(1).strip() if caption_match else text.strip()
        tags = (
            [tag.strip() for tag in tags_match.group(1).split(",") if tag.strip()]
            if tags_match
            else []
        )

        logger.info(
            "[GeminiVisionClient] model=%s caption=%r tags=%s", model_used, caption, tags
        )
        return caption, tags


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
