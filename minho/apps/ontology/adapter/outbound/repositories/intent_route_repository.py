from __future__ import annotations

from ontology.app.ports.output.intent_route_repository_port import IntentRouteRepositoryPort
from ontology.domain.intent_route import IntentRoute

_ROUTES: list[IntentRoute] = [
    IntentRoute(label="인사", example_utterances=["안녕", "안녕하세요", "반가워", "하이"]),
    IntentRoute(
        label="질문",
        example_utterances=["이게 뭐야?", "어떻게 해야 해?", "왜 그런 거야?", "설명해줘"],
    ),
    IntentRoute(
        label="요청",
        example_utterances=["이거 해줘", "만들어줘", "정리해줘", "번역해줘"],
    ),
    IntentRoute(
        label="잡담",
        example_utterances=["오늘 날씨 어때", "심심하다", "재밌는 얘기 해줘", "너는 누구야"],
    ),
    IntentRoute(
        label="불만",
        example_utterances=["왜 안 돼", "짜증나", "이거 고쳐줘", "너무 느려"],
    ),
]


class InMemoryIntentRouteRepository(IntentRouteRepositoryPort):
    """미리 정의된 의도(route)와 예시 발화 — DB 없이 코드에 고정된 목록."""

    async def list_routes(self) -> list[IntentRoute]:
        return list(_ROUTES)
