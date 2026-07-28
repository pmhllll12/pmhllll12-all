from __future__ import annotations

from abc import ABC, abstractmethod

from admin.app.dtos.langchain_chat_dto import ChatMessageResult, SendChatMessageCommand


class LangchainChatUseCase(ABC):
    @abstractmethod
    async def send_message(self, command: SendChatMessageCommand) -> ChatMessageResult:
        """사용자 메시지를 LangChain 체인으로 보내 답변을 받는다."""
        raise NotImplementedError
