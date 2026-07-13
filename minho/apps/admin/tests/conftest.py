from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from admin.adapter.inbound.api import silicon_valley_router

from database import get_db


async def _override_get_db() -> AsyncGenerator[None]:
    yield None


@pytest.fixture()
def client() -> TestClient:
    app = FastAPI()
    app.include_router(silicon_valley_router)
    app.dependency_overrides[get_db] = _override_get_db
    return TestClient(app)


@pytest.fixture()
def anyio_backend() -> str:
    """repository 의 async 메소드를 테스트할 때 사용하는 anyio 백엔드 고정."""
    return "asyncio"
