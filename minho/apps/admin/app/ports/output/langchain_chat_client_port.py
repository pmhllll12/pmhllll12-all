from __future__ import annotations

from abc import ABC, abstractmethod


class LangchainChatClientPort(ABC):
    @abstractmethod
    async def generate_reply(self, message: str) -> tuple[str, str]:
        """자유 대화 메시지에 대한 (답변, 모델명)을 반환한다."""
        raise NotImplementedError
