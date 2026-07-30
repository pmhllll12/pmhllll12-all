from __future__ import annotations

from abc import ABC, abstractmethod


class EmbeddingPort(ABC):
    """텍스트 → 벡터 변환. 구현은 adapter/outbound 의 임베딩 클라이언트."""

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        raise NotImplementedError


__all__ = ["EmbeddingPort"]
