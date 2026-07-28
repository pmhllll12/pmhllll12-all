from __future__ import annotations

from admin.adapter.outbound.client.langchain_chat_client import LangchainOllamaChatClient
from admin.app.ports.input.langchain_chat_use_case import LangchainChatUseCase
from admin.app.ports.output.langchain_chat_client_port import LangchainChatClientPort
from admin.app.use_cases.langchain_chat_interactor import LangchainChatInteractor
from fastapi import Depends


def get_langchain_chat_client_port() -> LangchainChatClientPort:
    return LangchainOllamaChatClient()


def get_langchain_chat_use_case(
    client: LangchainChatClientPort = Depends(get_langchain_chat_client_port),
) -> LangchainChatUseCase:
    return LangchainChatInteractor(client=client)
