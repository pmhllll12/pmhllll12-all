from __future__ import annotations

from functools import lru_cache

from fastapi import Depends
from ontology.adapter.outbound.gemini_chatbot_engine import GeminiChatbotEngine
from ontology.adapter.outbound.repositories.intent_route_repository import (
    InMemoryIntentRouteRepository,
)
from ontology.adapter.outbound.semantic_intent_classifier import SemanticIntentClassifier
from ontology.app.ports.input.semantic_chat_use_case import SemanticChatUseCase
from ontology.app.ports.output.chatbot_engine_port import ChatbotEnginePort
from ontology.app.ports.output.intent_route_repository_port import IntentRouteRepositoryPort
from ontology.app.ports.output.semantic_intent_classifier_port import SemanticIntentClassifierPort
from ontology.app.use_cases.semantic_chat_interactor import SemanticChatInteractor


@lru_cache
def get_intent_route_repository() -> IntentRouteRepositoryPort:
    return InMemoryIntentRouteRepository()


@lru_cache
def get_semantic_intent_classifier(
    repository: IntentRouteRepositoryPort = Depends(get_intent_route_repository),
) -> SemanticIntentClassifierPort:
    # 프로세스당 하나만 유지 — route 예시 발화 임베딩 캐시가 요청마다 새로 계산되지 않도록.
    return SemanticIntentClassifier(route_repository=repository)


@lru_cache
def get_chatbot_engine() -> ChatbotEnginePort:
    return GeminiChatbotEngine()


def get_semantic_chat_use_case(
    classifier: SemanticIntentClassifierPort = Depends(get_semantic_intent_classifier),
    engine: ChatbotEnginePort = Depends(get_chatbot_engine),
) -> SemanticChatUseCase:
    return SemanticChatInteractor(classifier=classifier, engine=engine)
