from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime

from ontology.app.dtos.vision_dto import StoredImage


class VisionPort(ABC):
    @abstractmethod
    async def save(
        self,
        filename: str,
        caption: str,
        tags: list[str],
        image_key: str,
        analyzed_at: datetime,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def list_recent(self, limit: int = 100) -> list[StoredImage]:
        raise NotImplementedError
