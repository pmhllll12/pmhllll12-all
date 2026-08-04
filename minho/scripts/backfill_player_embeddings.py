"""`moneyball_players.embedding` 백필 CLI.

    cd minho
    python scripts/backfill_player_embeddings.py --dry-run     # 대상 건수·샘플 텍스트만
    python scripts/backfill_player_embeddings.py               # 실제 임베딩 채우기

`.env` 의 `DATABASE_URL` 과 `GEMINI_API_KEY` 가 필요하다. 이미 채워진 행은 건드리지
않으므로(`--overwrite` 제외) 중간에 끊겨도 그냥 다시 실행하면 이어서 채운다.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# main.py 와 같은 sys.path 구성 — `moneyball`·`core` 최상위 임포트를 위해 필요
_BACKEND_ROOT = Path(__file__).resolve().parent.parent
for _path in (str(_BACKEND_ROOT), str(_BACKEND_ROOT / "apps"), str(_BACKEND_ROOT / "core")):
    if _path not in sys.path:
        sys.path.append(_path)

from moneyball.adapter.outbound.gemini_embedding_client import (  # noqa: E402
    GeminiEmbeddingClient,
)
from moneyball.adapter.outbound.repositories.player_embedding_repository import (  # noqa: E402
    PlayerEmbeddingRepository,
)
from moneyball.app.dtos.player_embedding_dto import BackfillCommand  # noqa: E402
from moneyball.app.use_cases.player_embedding_backfill_interactor import (  # noqa: E402
    PlayerEmbeddingBackfillInteractor,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker  # noqa: E402

import database  # noqa: E402
from logging_config import setup_app_logging  # noqa: E402

logger = logging.getLogger("backfill_player_embeddings")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="moneyball_players.embedding 백필")
    parser.add_argument("--limit", type=int, default=None, help="처리할 최대 선수 수 (기본: 전부)")
    parser.add_argument("--batch-size", type=int, default=20, help="배치 크기·커밋 단위 (기본 20)")
    parser.add_argument(
        "--sleep",
        type=float,
        default=0.0,
        help="임베딩 호출 사이 대기 초 (무료 티어 rate limit 완화)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="임베딩·저장 없이 대상 건수와 샘플 텍스트만 출력",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="이미 임베딩이 있는 선수도 다시 생성",
    )
    return parser.parse_args(argv)


async def _run(args: argparse.Namespace) -> int:
    session_factory = database.AsyncSessionLocal
    if session_factory is None:
        logger.error("DATABASE_URL 이 없거나 DB 엔진 초기화에 실패했습니다 (.env 확인).")
        return 1

    command = BackfillCommand(
        limit=args.limit,
        batch_size=args.batch_size,
        overwrite=args.overwrite,
        sleep_seconds=args.sleep,
        dry_run=args.dry_run,
    )

    try:
        return await _backfill(session_factory, command)
    finally:
        # 엔진을 만든 이벤트 루프 안에서 정리한다 (루프 밖 dispose 는 경고·오류를 낸다).
        await database.dispose_engine()


async def _backfill(
    session_factory: async_sessionmaker[AsyncSession], command: BackfillCommand
) -> int:
    async with session_factory() as session:
        repository = PlayerEmbeddingRepository(session)
        missing_before = await repository.count_missing()
        logger.info("임베딩이 비어 있는 선수: %d명", missing_before)

        interactor = PlayerEmbeddingBackfillInteractor(
            players=repository, embeddings=GeminiEmbeddingClient()
        )
        result = await interactor.backfill(command)

        logger.info(
            "대상 %d명 / 채움 %d명 / 건너뜀(이름 없음) %d명 / 실패 %d명",
            result.targeted,
            result.updated,
            result.skipped,
            result.failed,
        )
        for preview in result.previews:
            logger.info("샘플 임베딩 텍스트: %s", preview)

        if not command.dry_run:
            logger.info("남은 NULL 임베딩: %d명", await repository.count_missing())

    return 1 if result.failed else 0


def main(argv: list[str] | None = None) -> int:
    setup_app_logging()
    return asyncio.run(_run(_parse_args(argv)))


if __name__ == "__main__":
    raise SystemExit(main())
