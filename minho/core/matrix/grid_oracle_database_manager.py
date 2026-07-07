"""Matrix 측 Neon/PostgreSQL — 루트 `database` 모듈과 동일 엔진·Base.

타이타닉 James ORM(`JamesPerson`, `JamesBooking`)은 `database.Base` 에 등록됩니다.
Alembic·`create_all` 은 `database` 또는 이 모듈을 통해 동일 메타데이터를 사용합니다.
"""

from __future__ import annotations

from database import (  # noqa: F401
    AsyncSessionLocal,
    Base,
    alembic_database_url,
    create_all_tables,
    dispose_engine,
    engine,
    get_db,
    get_db_optional,
    get_db_session,
)

__all__ = [
    "AsyncSessionLocal",
    "Base",
    "alembic_database_url",
    "create_all_tables",
    "dispose_engine",
    "engine",
    "get_db",
    "get_db_optional",
    "get_db_session",
]
