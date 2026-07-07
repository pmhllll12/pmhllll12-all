from __future__ import annotations

from abc import ABC, abstractmethod


class EmailClientPort(ABC):
    @abstractmethod
    async def deliver(self, to_email: str, topic: str) -> bool:
        raise NotImplementedError
