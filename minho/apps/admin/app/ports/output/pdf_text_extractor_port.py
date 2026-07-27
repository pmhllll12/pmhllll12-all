from __future__ import annotations

from abc import ABC, abstractmethod


class PdfTextExtractorPort(ABC):
    @abstractmethod
    async def extract(self, content: bytes, filename: str) -> str:
        """PDF 바이트에서 텍스트를 추출한다."""
        raise NotImplementedError
