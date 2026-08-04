from __future__ import annotations

from abc import ABC, abstractmethod

from moneyball.app.dtos.player_embedding_dto import BackfillCommand, BackfillResult


class PlayerEmbeddingBackfillUseCase(ABC):
    @abstractmethod
    async def backfill(self, command: BackfillCommand) -> BackfillResult:
        raise NotImplementedError


__all__ = ["PlayerEmbeddingBackfillUseCase"]
