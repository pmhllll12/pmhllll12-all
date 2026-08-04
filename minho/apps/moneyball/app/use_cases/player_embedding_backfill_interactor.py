"""`moneyball_players.embedding` 백필 — 프로필 텍스트를 임베딩해 채운다."""

from __future__ import annotations

import asyncio
import logging

from moneyball.app.dtos.player_embedding_dto import (
    BackfillCommand,
    BackfillResult,
    PlayerProfile,
)
from moneyball.app.ports.input.player_embedding_backfill_use_case import (
    PlayerEmbeddingBackfillUseCase,
)
from moneyball.app.ports.output.embedding_port import EmbeddingPort
from moneyball.app.ports.output.player_embedding_port import PlayerEmbeddingPort

logger = logging.getLogger(__name__)

# dry-run 에서 눈으로 확인할 샘플 텍스트 개수
_PREVIEW_LIMIT = 3


class PlayerEmbeddingBackfillInteractor(PlayerEmbeddingBackfillUseCase):
    def __init__(self, players: PlayerEmbeddingPort, embeddings: EmbeddingPort) -> None:
        self.players = players
        self.embeddings = embeddings

    async def backfill(self, command: BackfillCommand) -> BackfillResult:
        targeted = updated = skipped = failed = 0
        previews: list[str] = []
        remaining = command.limit
        cursor: str | None = None

        while True:
            batch_size = command.batch_size
            if remaining is not None:
                batch_size = min(batch_size, remaining)
            if batch_size <= 0:
                break

            batch = await self.players.list_targets(
                limit=batch_size, overwrite=command.overwrite, after_player_id=cursor
            )
            if not batch:
                break

            targeted += len(batch)
            if remaining is not None:
                remaining -= len(batch)
            cursor = batch[-1].player_id

            saved_in_batch = 0
            for profile in batch:
                text = profile.to_embedding_text()
                if not text:
                    skipped += 1
                    logger.info(
                        "[PlayerEmbeddingBackfill] skip player_id=%s (이름 없음)",
                        profile.player_id,
                    )
                    continue

                if command.dry_run:
                    if len(previews) < _PREVIEW_LIMIT:
                        previews.append(text)
                    continue

                vector = await self._embed(profile, text)
                if vector is None:
                    failed += 1
                    continue

                await self.players.save_embedding(profile.player_id, vector)
                saved_in_batch += 1
                updated += 1

                if command.sleep_seconds > 0:
                    await asyncio.sleep(command.sleep_seconds)

            if saved_in_batch:
                await self.players.commit()
                logger.info(
                    "[PlayerEmbeddingBackfill] 배치 커밋 %d건 (누적 updated=%d)",
                    saved_in_batch,
                    updated,
                )

        return BackfillResult(
            targeted=targeted,
            updated=updated,
            skipped=skipped,
            failed=failed,
            previews=previews,
        )

    async def _embed(self, profile: PlayerProfile, text: str) -> list[float] | None:
        """한 선수의 실패가 전체 백필을 멈추지 않도록 여기서 흡수한다."""
        try:
            return await self.embeddings.embed(text)
        except Exception as exc:  # noqa: BLE001 - 개별 실패는 집계만 하고 계속 진행
            logger.warning(
                "[PlayerEmbeddingBackfill] embed 실패 player_id=%s: %s", profile.player_id, exc
            )
            return None


__all__ = ["PlayerEmbeddingBackfillInteractor"]
