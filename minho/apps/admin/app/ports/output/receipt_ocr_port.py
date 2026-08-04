from __future__ import annotations

from abc import ABC, abstractmethod


class ReceiptOcrPort(ABC):
    @abstractmethod
    async def extract_text(self, content: bytes, mime_type: str) -> str:
        """영수증 이미지에서 텍스트를 그대로 읽어 돌려준다."""
        raise NotImplementedError
