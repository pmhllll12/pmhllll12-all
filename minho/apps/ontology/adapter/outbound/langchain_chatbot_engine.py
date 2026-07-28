from __future__ import annotations

import logging
import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from ontology.adapter.outbound.ollama_errors import OllamaUnavailableError
from ontology.app.ports.output.chatbot_engine_port import ChatbotEnginePort
from ontology.domain.chat_intent import ChatIntent

logger = logging.getLogger(__name__)

_DEFAULT_OLLAMA_HOST = "http://localhost:11434"
_DEFAULT_OLLAMA_MODEL = "qwen2.5:3b"

_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "당신은 친절하고 간결하게 답하는 어시스턴트입니다. "
            "사용자 메시지의 의도는 '{intent_label}'로 판정되었습니다 — 이를 참고해 답하세요.",
        ),
        ("human", "{message}"),
    ]
)


class LangchainChatbotEngine(ChatbotEnginePort):
    """LangChain LCEL 체인(`prompt | llm | parser`)으로, 판정된 의도를 참고해 답하는 챗봇 엔진."""

    def __init__(self) -> None:
        self._host = os.getenv("OLLAMA_HOST", _DEFAULT_OLLAMA_HOST)
        self._model = os.getenv("OLLAMA_MODEL") or _DEFAULT_OLLAMA_MODEL
        llm = ChatOllama(base_url=self._host, model=self._model)
        self._chain = _PROMPT | llm | StrOutputParser()

    async def generate_reply(self, message: str, intent: ChatIntent) -> tuple[str, str]:
        try:
            reply = await self._chain.ainvoke(
                {"message": message, "intent_label": intent.label}
            )
        except Exception as exc:  # noqa: BLE001 — 외부 서비스 경계, 원인 불문 상위에서 503 등으로 변환
            logger.warning("[LangchainChatbotEngine] Ollama 호출 실패: %s", exc)
            raise OllamaUnavailableError(
                f"Ollama 서버({self._host})에 연결할 수 없습니다."
            ) from exc
        return reply.strip(), self._model
