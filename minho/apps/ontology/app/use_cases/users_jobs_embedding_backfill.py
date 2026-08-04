"""ontology_users / ontology_jobs 의 embedding 컬럼 백필 로직 (순수 함수).

DB·Gemini 접근은 호출자가 주입한다. 그래야 테스트가 외부 의존 없이 돈다.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass

from ontology.app.ports.output.embedding_port import EmbeddingPort

logger = logging.getLogger(__name__)

EMBEDDING_DIM = 768


@dataclass(frozen=True)
class BackfillResult:
    filled: int = 0
    failed: int = 0


def build_user_text(name: str, age: int | None) -> str:
    """사용자 임베딩용 텍스트. 나이가 없으면 이름만 쓴다."""
    if age is None:
        return name
    return f"{name} {age}세"


def build_job_text(title: str, company: str) -> str:
    return f"{title} {company}"


async def backfill_rows(
    rows: Sequence[tuple[int, str]],
    embedder: EmbeddingPort,
    save: Callable[[int, list[float]], Awaitable[None]],
    dim: int = EMBEDDING_DIM,
) -> BackfillResult:
    """(id, 텍스트) 목록을 임베딩해 저장한다.

    한 행이 실패해도 나머지를 계속 처리한다 — 남은 NULL 은 재실행으로 채운다.
    """
    filled = failed = 0

    for row_id, text in rows:
        try:
            vector = await embedder.embed(text)
        except Exception as exc:
            logger.warning("[backfill] id=%s 임베딩 실패: %s", row_id, exc)
            failed += 1
            continue

        if len(vector) != dim:
            logger.warning(
                "[backfill] id=%s 차원 불일치 (기대 %d, 실제 %d) — 저장하지 않음",
                row_id,
                dim,
                len(vector),
            )
            failed += 1
            continue

        await save(row_id, vector)
        filled += 1

    return BackfillResult(filled=filled, failed=failed)
