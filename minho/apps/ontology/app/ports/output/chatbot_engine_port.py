from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.domain.chat_intent import ChatIntent


class ChatbotEnginePort(ABC):
    @abstractmethod
    async def generate_reply(self, message: str, intent: ChatIntent) -> tuple[str, str]:
        """판정된 의도를 참고해 (답변, 모델명)을 생성한다."""
        raise NotImplementedError
