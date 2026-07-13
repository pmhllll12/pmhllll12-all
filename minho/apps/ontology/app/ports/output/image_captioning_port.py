from __future__ import annotations

from abc import ABC, abstractmethod


class ImageCaptioningPort(ABC):
    @abstractmethod
    async def caption(self, content: bytes, mime_type: str) -> tuple[str, list[str]]:
        """이미지를 분석해 (설명, 태그 목록)을 반환한다."""
        raise NotImplementedError
