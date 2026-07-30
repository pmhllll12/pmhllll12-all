#!/usr/bin/env python3
"""ontology_users / ontology_jobs 의 embedding 을 Gemini 로 채운다.

embedding IS NULL 인 행만 처리하므로 재실행이 안전하다.

실행 (backend 컨테이너, 작업 디렉터리 /app):
    docker exec pmhllll12-all-backend-1 \
        python apps/ontology/scripts/backfill_users_jobs_embedding.py
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

_ONTOLOGY_ROOT = Path(__file__).resolve().parents[1]
_APPS_ROOT = _ONTOLOGY_ROOT.parent
_MINHO_ROOT = _APPS_ROOT.parent
for _path in (str(_MINHO_ROOT), str(_APPS_ROOT)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("backfill_users_jobs_embedding")

from database import AsyncSessionLocal  # noqa: E402
from ontology.adapter.outbound.gemini_embedding_client import (  # noqa: E402
    GeminiEmbeddingClient,
)
from ontology.app.use_cases.users_jobs_embedding_backfill import (  # noqa: E402
    backfill_rows,
    build_job_text,
    build_user_text,
)
from sqlalchemy import text  # noqa: E402


async def main() -> int:
    if AsyncSessionLocal is None:
        logger.error("DATABASE_URL 이 없어 DB 세션을 만들 수 없습니다.")
        return 1

    embedder = GeminiEmbeddingClient()

    async with AsyncSessionLocal() as session:
        user_rows = (
            await session.execute(
                text(
                    "SELECT id, name, age FROM ontology_users "
                    "WHERE embedding IS NULL ORDER BY id"
                )
            )
        ).all()
        job_rows = (
            await session.execute(
                text(
                    "SELECT id, title, company FROM ontology_jobs "
                    "WHERE embedding IS NULL ORDER BY id"
                )
            )
        ).all()

        async def save_user(row_id: int, vector: list[float]) -> None:
            await session.execute(
                text(
                    "UPDATE ontology_users SET embedding = CAST(:v AS vector) WHERE id = :id"
                ),
                {"v": str(vector), "id": row_id},
            )

        async def save_job(row_id: int, vector: list[float]) -> None:
            await session.execute(
                text(
                    "UPDATE ontology_jobs SET embedding = CAST(:v AS vector) WHERE id = :id"
                ),
                {"v": str(vector), "id": row_id},
            )

        user_result = await backfill_rows(
            [(r.id, build_user_text(r.name, r.age)) for r in user_rows],
            embedder,
            save_user,
        )
        job_result = await backfill_rows(
            [(r.id, build_job_text(r.title, r.company)) for r in job_rows],
            embedder,
            save_job,
        )
        await session.commit()

    logger.info(
        "users filled=%d failed=%d / jobs filled=%d failed=%d",
        user_result.filled,
        user_result.failed,
        job_result.filled,
        job_result.failed,
    )
    return 1 if (user_result.failed or job_result.failed) else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
