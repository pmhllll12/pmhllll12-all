from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.app.dtos.semantic_chat_dto import SemanticChatResult, SendSemanticChatCommand


class SemanticChatUseCase(ABC):
    @abstractmethod
    async def handle_message(self, command: SendSemanticChatCommand) -> SemanticChatResult:
        """메시지의 의도를 판정한 뒤 그 의도를 참고해 챗봇 엔진으로 답한다."""
        raise NotImplementedError
