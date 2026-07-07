from __future__ import annotations

from abc import ABC, abstractmethod


class ContentFilterPort(ABC):
    @abstractmethod
    async def is_normal(self, content: str) -> bool:
        raise NotImplementedError
