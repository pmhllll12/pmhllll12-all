from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from admin.app.dtos.pdf_loader_dto import PdfSummaryLog


class PdfLoaderPort(ABC):
    @abstractmethod
    async def save(
        self,
        filename: str,
        char_count: int,
        summary: str,
        uploaded_at: datetime,
    ) -> None:
        """레포지토리 저장 추상 메소드"""
        raise NotImplementedError

    @abstractmethod
    async def list_recent(self, limit: int = 100) -> list[PdfSummaryLog]:
        """레포지토리 최근 이력 조회 추상 메소드"""
        raise NotImplementedError
