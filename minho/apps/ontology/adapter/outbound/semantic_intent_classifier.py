from __future__ import annotations

import asyncio
import logging

import numpy as np
from ontology.app.ports.output.intent_route_repository_port import IntentRouteRepositoryPort
from ontology.app.ports.output.semantic_intent_classifier_port import SemanticIntentClassifierPort
from ontology.domain.chat_intent import ChatIntent
from ontology.domain.intent_route import IntentRoute

from core.matrix.vault_keymaker_secret_manager import keymaker

logger = logging.getLogger(__name__)


class SemanticIntentClassifier(SemanticIntentClassifierPort):
    """route 예시 발화를 Gemini 임베딩으로 변환해, 메시지와 코사인 유사도가 가장 가까운 의도로
    분류한다."""

    def __init__(self, route_repository: IntentRouteRepositoryPort) -> None:
        self._route_repository = route_repository
        self._route_vectors: list[tuple[IntentRoute, np.ndarray]] | None = None

    async def classify(self, message: str) -> ChatIntent:
        route_vectors = await self._get_route_vectors()
        message_vector = np.array(await asyncio.to_thread(keymaker.embed_content, message))

        best_route, best_score = max(
            (
                (route, float(_cosine_similarity(message_vector, vectors).max()))
                for route, vectors in route_vectors
            ),
            key=lambda item: item[1],
        )
        return ChatIntent(
            label=best_route.label,
            confidence=round(best_score, 4),
            reason=f"예시 발화와의 코사인 유사도 최고값={best_score:.4f}",
        )

    async def _get_route_vectors(self) -> list[tuple[IntentRoute, np.ndarray]]:
        """route별 예시 발화 임베딩 — 요청마다 재계산하지 않도록 최초 1회만 캐시한다."""
        if self._route_vectors is not None:
            return self._route_vectors

        routes = await self._route_repository.list_routes()
        route_vectors: list[tuple[IntentRoute, np.ndarray]] = []
        for route in routes:
            embeddings = [
                await asyncio.to_thread(keymaker.embed_content, utterance)
                for utterance in route.example_utterances
            ]
            route_vectors.append((route, np.array(embeddings)))
        logger.info("[SemanticIntentClassifier] route 임베딩 캐시 생성: %d개", len(route_vectors))
        self._route_vectors = route_vectors
        return route_vectors


def _cosine_similarity(vector: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    vector_norm = vector / (np.linalg.norm(vector) + 1e-10)
    matrix_norm = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10)
    return matrix_norm @ vector_norm
