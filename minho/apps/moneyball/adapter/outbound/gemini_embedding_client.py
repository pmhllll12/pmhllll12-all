"""선수 프로필 텍스트 → 768차원 벡터 (Gemini, pgvector 저장용)."""

from __future__ import annotations

import asyncio
import logging

from moneyball.adapter.outbound.orm.player_orm import EMBEDDING_DIM
from moneyball.app.ports.output.embedding_port import EmbeddingPort

from core.matrix.vault_keymaker_secret_manager import (
    MissingApiKeyError,
    format_gemini_error,
    keymaker,
)

logger = logging.getLogger(__name__)

_DEFAULT_MAX_ATTEMPTS = 4
_DEFAULT_BASE_DELAY_SECONDS = 2.0


class GeminiEmbeddingClient(EmbeddingPort):
    """무료 티어 할당량(429) 은 지수 백오프로 재시도, 그 외 오류는 그대로 올린다."""

    def __init__(
        self,
        max_attempts: int = _DEFAULT_MAX_ATTEMPTS,
        base_delay_seconds: float = _DEFAULT_BASE_DELAY_SECONDS,
    ) -> None:
        self._max_attempts = max(1, max_attempts)
        self._base_delay_seconds = base_delay_seconds

    async def embed(self, text: str) -> list[float]:
        delay = self._base_delay_seconds

        for attempt in range(1, self._max_attempts + 1):
            try:
                vector = await asyncio.to_thread(keymaker.embed_content, text)
            except MissingApiKeyError:
                # 키가 없으면 재시도해도 소용없고 전체 실행을 멈춰야 한다.
                raise
            except Exception as exc:
                status, message = format_gemini_error(exc)
                if status != 429 or attempt == self._max_attempts:
                    raise
                logger.warning(
                    "[GeminiEmbeddingClient] 할당량 초과 — %.1f초 후 재시도 (%d/%d): %s",
                    delay,
                    attempt,
                    self._max_attempts,
                    message,
                )
                await asyncio.sleep(delay)
                delay *= 2
                continue

            if len(vector) != EMBEDDING_DIM:
                raise ValueError(
                    f"임베딩 차원이 컬럼 정의와 다릅니다: {len(vector)} != {EMBEDDING_DIM}"
                )
            return vector

        raise RuntimeError("임베딩 재시도를 모두 소진했습니다.")


__all__ = ["GeminiEmbeddingClient"]
