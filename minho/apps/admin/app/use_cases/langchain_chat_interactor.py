from __future__ import annotations

from admin.app.dtos.langchain_chat_dto import ChatMessageResult, SendChatMessageCommand
from admin.app.ports.input.langchain_chat_use_case import LangchainChatUseCase
from admin.app.ports.output.langchain_chat_client_port import LangchainChatClientPort


class LangchainChatInteractor(LangchainChatUseCase):
    def __init__(self, client: LangchainChatClientPort) -> None:
        self._client = client

    async def send_message(self, command: SendChatMessageCommand) -> ChatMessageResult:
        reply, model = await self._client.generate_reply(command.message)
        return ChatMessageResult(reply=reply, model=model)
