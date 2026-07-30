"""Gemini 임베딩으로 텍스트를 벡터로 변환한다 (pgvector 저장용).

community 앱에 같은 역할의 클라이언트가 있지만 import-linter contract 2 가
ontology → community 를 금지하므로 여기에 따로 둔다. core.matrix 는 참조 가능하다.
"""

from __future__ import annotations

import asyncio
import logging

from core.matrix.vault_keymaker_secret_manager import keymaker

logger = logging.getLogger(__name__)


class GeminiEmbeddingClient:
    async def embed(self, text: str) -> list[float]:
        vector = await asyncio.to_thread(keymaker.embed_content, text)
        logger.info("[GeminiEmbeddingClient] embed dim=%d", len(vector))
        return vector
