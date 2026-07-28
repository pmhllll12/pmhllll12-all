from __future__ import annotations

from abc import ABC, abstractmethod

from ontology.domain.intent_route import IntentRoute


class IntentRouteRepositoryPort(ABC):
    @abstractmethod
    async def list_routes(self) -> list[IntentRoute]:
        """시멘틱 라우팅에 쓸 의도(route) 정의 목록을 반환한다."""
        raise NotImplementedError
