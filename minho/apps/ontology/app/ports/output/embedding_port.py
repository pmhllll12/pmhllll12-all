"""텍스트 → 벡터 변환 포트. community 앱의 동명 포트를 재사용할 수 없다 —
import-linter contract 2 가 ontology → community 를 금지한다."""

from __future__ import annotations

from typing import Protocol


class EmbeddingPort(Protocol):
    async def embed(self, text: str) -> list[float]: ...
