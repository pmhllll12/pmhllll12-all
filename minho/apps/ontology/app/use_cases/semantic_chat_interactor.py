from __future__ import annotations

from ontology.app.dtos.semantic_chat_dto import SemanticChatResult, SendSemanticChatCommand
from ontology.app.ports.input.semantic_chat_use_case import SemanticChatUseCase
from ontology.app.ports.output.chatbot_engine_port import ChatbotEnginePort
from ontology.app.ports.output.semantic_intent_classifier_port import SemanticIntentClassifierPort


class SemanticChatInteractor(SemanticChatUseCase):
    def __init__(
        self,
        classifier: SemanticIntentClassifierPort,
        engine: ChatbotEnginePort,
    ) -> None:
        self._classifier = classifier
        self._engine = engine

    async def handle_message(self, command: SendSemanticChatCommand) -> SemanticChatResult:
        intent = await self._classifier.classify(command.message)
        reply, model = await self._engine.generate_reply(command.message, intent)
        return SemanticChatResult(
            intent_label=intent.label,
            intent_confidence=intent.confidence,
            reply=reply,
            model=model,
        )
