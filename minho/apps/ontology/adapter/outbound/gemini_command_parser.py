from __future__ import annotations

import asyncio
import logging
import re
from typing import Any

from ontology.app.dtos.command_parser_dto import ParsedCommand
from ontology.app.ports.output.command_parser_port import CommandParserPort

from core.matrix.vault_keymaker_secret_manager import keymaker

logger = logging.getLogger(__name__)

_DEFAULT_MAX_DEPTH = 2
_DEFAULT_MAX_PAGES = 30
_MAX_DEPTH_CAP = 3
_MAX_PAGES_CAP = 50

_PROMPT_TEMPLATE = (
    "당신은 웹 크롤러/스크래퍼 설정을 돕는 도우미입니다.\n"
    "대상 사이트: {website}\n"
    "사용자 명령: {command}\n\n"
    "이 명령에서 검색할 핵심 키워드와 크롤링 범위를 추출하세요.\n"
    "반드시 아래 형식으로만 답하세요:\n"
    "KEYWORD: <검색할 핵심 키워드 (짧은 단어/구절)>\n"
    "MAX_DEPTH: <내부 링크를 따라갈 단계 수, 1~3 사이 정수>\n"
    "MAX_PAGES: <최대로 수집할 페이지 수, 1~50 사이 정수>"
)

_KEYWORD_RE = re.compile(r"KEYWORD\s*:\s*(.+)")
_MAX_DEPTH_RE = re.compile(r"MAX_DEPTH\s*:\s*(\d+)")
_MAX_PAGES_RE = re.compile(r"MAX_PAGES\s*:\s*(\d+)")


class GeminiCommandParser(CommandParserPort):
    """Gemini로 자연어 명령어에서 keyword·크롤링 범위(max_depth, max_pages)를 추출한다."""

    async def parse(self, website: str, command: str) -> ParsedCommand:
        prompt = _PROMPT_TEMPLATE.format(website=website, command=command)
        response, model_used = await asyncio.to_thread(keymaker.generate_content, prompt)
        text = _extract_text(response)

        keyword_match = _KEYWORD_RE.search(text)
        depth_match = _MAX_DEPTH_RE.search(text)
        pages_match = _MAX_PAGES_RE.search(text)

        keyword = keyword_match.group(1).strip() if keyword_match else command.strip()
        max_depth = (
            _clamp(int(depth_match.group(1)), 1, _MAX_DEPTH_CAP)
            if depth_match
            else _DEFAULT_MAX_DEPTH
        )
        max_pages = (
            _clamp(int(pages_match.group(1)), 1, _MAX_PAGES_CAP)
            if pages_match
            else _DEFAULT_MAX_PAGES
        )

        logger.info(
            "[GeminiCommandParser] model=%s website=%r command=%r -> keyword=%r "
            "max_depth=%d max_pages=%d",
            model_used,
            website,
            command,
            keyword,
            max_depth,
            max_pages,
        )
        return ParsedCommand(keyword=keyword, max_depth=max_depth, max_pages=max_pages)


def _clamp(value: int, low: int, high: int) -> int:
    return max(low, min(high, value))


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
