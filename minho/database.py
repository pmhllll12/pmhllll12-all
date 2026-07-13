"""Neon PostgreSQL 비동기 연결 — FastAPI → 아웃바운드 레포지토리까지의 DB 통로."""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from collections.abc import AsyncGenerator
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

# Windows: psycopg 비동기는 ProactorEventLoop 와 호환되지 않음
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

# 1. DB 엔진 (Neon 미설정 시 None — API 일부만 동작)
engine = None

# 2. 세션 팩토리 (Gemini 예시의 async_session 과 동일 역할)
AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None


class Base(DeclarativeBase):
    """ORM 모델 베이스 — `infrastructure/models.py` 의 Base 와 동일 개념."""


def _ensure_sslmode(url: str) -> str:
    """Neon 클라우드: `sslmode=require` 가 없으면 붙입니다."""
    parsed = urlparse(url)
    if parsed.scheme not in ("postgresql", "postgres", "postgresql+psycopg"):
        return url
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if "sslmode" not in query:
        query["sslmode"] = "require"
    return urlunparse(parsed._replace(query=urlencode(query)))


def _async_database_url(url: str) -> str:
    """Neon `postgresql://` URL → 비동기 드라이버 `postgresql+psycopg://`."""
    url = _ensure_sslmode(url)
    if url.startswith("postgresql+psycopg://"):
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    return url


def _build_engine() -> None:
    """DATABASE_URL 이 있으면 엔진·세션 팩토리를 초기화합니다."""
    global engine, AsyncSessionLocal

    if not DATABASE_URL:
        logger.info("DATABASE_URL 미설정 — DB 엔진 생략")
        return

    try:
        async_url = _async_database_url(DATABASE_URL)
        echo = os.getenv("SQLALCHEMY_ECHO", "").lower() in ("1", "true", "yes")
        engine = create_async_engine(
            async_url,
            echo=echo,
            pool_pre_ping=True,
        )
        AsyncSessionLocal = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
        logger.info("Neon/PostgreSQL 비동기 엔진 준비 완료")
    except ModuleNotFoundError as exc:
        logger.warning(
            "DATABASE_URL 이 설정되어 있으나 psycopg 를 불러올 수 없습니다 (%s). "
            "`pip install -r requirements.txt` 를 실행하세요.",
            exc,
        )
        engine = None
        AsyncSessionLocal = None
    except Exception as exc:
        logger.warning("비동기 DB 엔진을 만들 수 없습니다: %s", exc)
        engine = None
        AsyncSessionLocal = None


_build_engine()


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """FastAPI Depends — 요청마다 세션을 열고 닫습니다 (③④ 단계에서 주입)."""
    if AsyncSessionLocal is None:
        if DATABASE_URL:
            raise HTTPException(
                status_code=503,
                detail=(
                    "DATABASE_URL 은 설정되어 있으나 PostgreSQL 드라이버(psycopg)를 "
                    "불러올 수 없습니다. `pip install -r requirements.txt` 후 서버를 다시 시작하세요."
                ),
            )
        raise HTTPException(
            status_code=503,
            detail="DATABASE_URL 이 .env 에 설정되지 않았습니다.",
        )
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            if session.in_transaction():
                await session.rollback()
            raise


async def get_db() -> AsyncGenerator[AsyncSession]:
    """기존 코드 호환용 별칭 (`get_db_session` 과 동일)."""
    async for session in get_db_session():
        yield session


async def get_db_optional() -> AsyncGenerator[AsyncSession | None]:
    """`DATABASE_URL` 이 없을 때는 `None` 을 넘겨 DB 없이도 라우트가 동작하도록 할 때 사용.

    `get_db_session` 을 async for 로 감싸지 않는다 — 중첩 제너레이터는 정리 시점에
    프록시 502·연결 오류를 유발할 수 있다.
    """
    if engine is None or AsyncSessionLocal is None:
        yield None
        return
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            if session.in_transaction():
                await session.rollback()
            raise


def alembic_database_url() -> str:
    """Alembic `env.py` 용 — `DATABASE_URL` 을 비동기 드라이버 URL 로 정규화."""
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL 이 설정되어 있지 않습니다.")
    return _async_database_url(DATABASE_URL)


async def create_all_tables() -> None:
    """등록된 ORM 메타데이터로 Neon 테이블 생성 (없을 때만)."""
    if engine is None:
        raise RuntimeError("DATABASE_URL 이 없거나 엔진 초기화에 실패했습니다.")

    from community.adapter.outbound.orm import juso_contact_orm, received_email_orm  # noqa: F401
    from ontology.adapter.outbound.orm import vision_orm  # noqa: F401
    from secom.app.models import user_model  # noqa: F401
    from titanic.adapter.outbound.orm import (
        booking_orm,  # noqa: F401
        person_orm,  # noqa: F401
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info(
        "DB create_all 완료 (secom_users, titanic_persons, titanic_bookings, "
        "community_juso_contacts, community_received_emails, vision_analyzed_images 등)"
    )


async def dispose_engine() -> None:
    """앱 종료 시 연결 풀 정리."""
    global engine, AsyncSessionLocal
    if engine is not None:
        await engine.dispose()
    engine = None
    AsyncSessionLocal = None


async def main() -> None:
    """Neon 연결·테이블 생성 스모크 테스트."""
    if engine is None or AsyncSessionLocal is None:
        raise RuntimeError(
            "DATABASE_URL 을 backend/.env 에 넣고 psycopg 를 설치한 뒤 다시 실행하세요."
        )

    from secom.app.models.user_model import User

    await create_all_tables()

    async with AsyncSessionLocal() as session:
        count_result = await session.execute(select(func.count()).select_from(User))
        total = int(count_result.scalar_one())
        logger.info("secom_users 행 수: %s", total)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
