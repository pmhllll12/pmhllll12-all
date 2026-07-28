from __future__ import annotations

import logging
import os

from admin.app.ports.output.langchain_chat_client_port import LangchainChatClientPort
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

logger = logging.getLogger(__name__)

_DEFAULT_OLLAMA_MODEL = "qwen2.5:3b"
_DEFAULT_OLLAMA_HOST = "http://localhost:11434"

_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "당신은 친절하고 간결하게 답하는 어시스턴트입니다."),
        ("human", "{message}"),
    ]
)


class OllamaUnavailableError(RuntimeError):
    """Ollama 서버에 연결할 수 없을 때."""


class LangchainOllamaChatClient(LangchainChatClientPort):
    """LangChain LCEL 체인(`prompt | llm | parser`)으로 Ollama와 자유 대화를 나눈다."""

    def __init__(self) -> None:
        self._host = os.getenv("OLLAMA_HOST", _DEFAULT_OLLAMA_HOST)
        self._model = os.getenv("OLLAMA_MODEL") or _DEFAULT_OLLAMA_MODEL
        llm = ChatOllama(base_url=self._host, model=self._model)
        self._chain = _PROMPT | llm | StrOutputParser()

    async def generate_reply(self, message: str) -> tuple[str, str]:
        try:
            reply = await self._chain.ainvoke({"message": message})
        except Exception as exc:  # noqa: BLE001 — 외부 서비스 경계, 원인 불문 503으로 변환
            logger.warning("[LangchainOllamaChatClient] Ollama 호출 실패: %s", exc)
            raise OllamaUnavailableError(
                f"Ollama 서버({self._host})에 연결할 수 없습니다. 서버가 켜져 있는지 확인하세요."
            ) from exc
        return reply.strip(), self._model
