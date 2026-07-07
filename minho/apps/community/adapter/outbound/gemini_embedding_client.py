from __future__ import annotations

import asyncio
import logging

from community.app.ports.output.embedding_port import EmbeddingPort
from core.matrix.vault_keymaker_secret_manager import keymaker

logger = logging.getLogger(__name__)


class GeminiEmbeddingClient(EmbeddingPort):
    """Gemini `text-embedding-004` 로 텍스트를 벡터로 변환 (pgvector 저장용)."""

    async def embed(self, text: str) -> list[float]:
        vector = await asyncio.to_thread(keymaker.embed_content, text)
        logger.info("[GeminiEmbeddingClient] embed dim=%d", len(vector))
        return vector
