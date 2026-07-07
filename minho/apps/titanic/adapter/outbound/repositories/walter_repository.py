"""Walter PostgreSQL 저장소 — 출력 포트 데이터 → Neon."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from titanic.adapter.outbound.orm.walter_passenger_orm import WalterPassenger
from titanic.app.ports.output.walter_port import (
    WalterPersistPayload,
    WalterPort,
)
from titanic.app.titanic_csv_parser import API_COLUMNS

logger = logging.getLogger(__name__)


async def ingest_persist_payload(
    session: AsyncSession,
    payload: WalterPersistPayload,
) -> int:
    """`walter_port.WalterPersistPayload` → Neon `titanic_walter_passengers`."""
    rows = payload.rows
    if not rows:
        logger.info("[walter_repository] 저장 스킵 — rows=0 filename=%s", payload.filename)
        return 0

    logger.info(
        "[walter_repository] Neon 저장 시작 — filename=%s rows=%s columns=%s",
        payload.filename,
        len(rows),
        ", ".join(payload.columns),
    )

    try:
        await session.execute(delete(WalterPassenger))
        session.add_all(
            WalterPassenger.from_record(payload.filename, row) for row in rows
        )
        await session.commit()
    except SQLAlchemyError as exc:
        await session.rollback()
        logger.exception("[walter_repository] Neon 저장 실패 — filename=%s", payload.filename)
        raise ValueError(f"Neon DB 저장에 실패했습니다: {exc}") from exc

    logger.info(
        "[walter_repository] Neon commit 완료 — titanic_walter_passengers %s행 (filename=%s)",
        len(rows),
        payload.filename,
    )
    return len(rows)


async def ingest_fetch_all_passengers(session: AsyncSession) -> list[dict[str, Any]]:
    """Neon → API 행 형식."""
    logger.info("[walter_repository] Neon 조회 시작 — titanic_walter_passengers")
    result = await session.execute(
        select(WalterPassenger).order_by(WalterPassenger.passenger_id)
    )
    passengers = result.scalars().all()
    rows = [p.to_api_row() for p in passengers]
    logger.info("[walter_repository] Neon 조회 완료 — %s행", len(rows))
    return rows


async def receive_persist_from_port(
    repository: WalterRepository,
    payload: WalterPersistPayload,
) -> int:
    """출력 포트 `submit_persist_upload` → PG 어댑터 수신."""
    logger.info(
        "[walter_repository] 수신 — persist filename=%s rows=%s",
        payload.filename,
        len(payload.rows),
    )
    return await repository.persist_payload(payload)


async def receive_fetch_from_port(repository: WalterRepository) -> list[dict[str, Any]]:
    """출력 포트 `submit_fetch_all_passengers` → PG 어댑터 수신."""
    logger.info("[walter_repository] 수신 — fetch_all")
    return await repository.load_all_rows()


class WalterRepository(WalterPort):
    """`WalterPort` 구현 — Neon PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        logger.info("[walter_repository] 인스턴스 생성 — session=%s", id(session))

    async def persist_payload(self, payload: WalterPersistPayload) -> int:
        logger.info(
            "[walter_repository] persist_payload — filename=%s → ingest_persist_payload",
            payload.filename,
        )
        return await ingest_persist_payload(self._session, payload)

    async def load_all_rows(self) -> list[dict[str, Any]]:
        logger.info("[walter_repository] load_all_rows → ingest_fetch_all_passengers")
        return await ingest_fetch_all_passengers(self._session)

    async def save_upload(
        self,
        *,
        filename: str,
        columns: list[str],
        rows: list[dict[str, Any]],
    ) -> int:
        logger.info(
            "[walter_repository] save_upload — filename=%s rows=%s → persist_payload",
            filename,
            len(rows),
        )
        return await self.persist_payload(
            WalterPersistPayload(filename=filename, columns=columns, rows=rows),
        )

    async def fetch_all(self) -> list[dict[str, Any]]:
        logger.info("[walter_repository] fetch_all → load_all_rows")
        return await self.load_all_rows()

    @staticmethod
    def api_columns() -> list[str]:
        return list(API_COLUMNS)
