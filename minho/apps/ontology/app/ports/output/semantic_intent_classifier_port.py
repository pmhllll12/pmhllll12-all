from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.domain.chat_intent import ChatIntent


class SemanticIntentClassifierPort(ABC):
    @abstractmethod
    async def classify(self, message: str) -> ChatIntent:
        """메시지를 저장된 의도(route) 중 의미상 가장 가까운 것으로 분류한다."""
        raise NotImplementedError
