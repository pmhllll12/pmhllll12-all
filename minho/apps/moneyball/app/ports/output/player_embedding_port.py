from __future__ import annotations

from abc import ABC, abstractmethod

from moneyball.app.dtos.player_embedding_dto import PlayerProfile


class PlayerEmbeddingPort(ABC):
    """`moneyball_players.embedding` 백필에 필요한 읽기·쓰기."""

    @abstractmethod
    async def list_targets(
        self, limit: int, overwrite: bool, after_player_id: str | None = None
    ) -> list[PlayerProfile]:
        """`player_id` 오름차순으로 `after_player_id` 다음 `limit` 건.

        `overwrite=False` 면 `embedding IS NULL` 인 행만 돌려준다. 커서로 페이징하는
        이유는 건너뛴·실패한 행이 계속 NULL 로 남아 offset 없이는 같은 배치를
        무한히 다시 읽게 되기 때문이다.
        """
        raise NotImplementedError

    @abstractmethod
    async def save_embedding(self, player_id: str, embedding: list[float]) -> None:
        """커밋은 하지 않는다 — 배치 단위로 `commit()` 을 호출한다."""
        raise NotImplementedError

    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError


__all__ = ["PlayerEmbeddingPort"]
