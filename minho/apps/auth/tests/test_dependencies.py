from __future__ import annotations

import asyncio

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from core import dependencies, security


def _make_request(
    headers: dict[str, str] | None = None, cookies: dict[str, str] | None = None
) -> Request:
    raw_headers = [(k.lower().encode(), v.encode()) for k, v in (headers or {}).items()]
    if cookies:
        cookie_header = "; ".join(f"{k}={v}" for k, v in cookies.items())
        raw_headers.append((b"cookie", cookie_header.encode()))
    scope = {
        "type": "http",
        "headers": raw_headers,
        "method": "GET",
        "path": "/",
        "query_string": b"",
    }
    return Request(scope)


@pytest.fixture(autouse=True)
def _reset_redis_singleton(monkeypatch, fake_redis):
    monkeypatch.setattr(dependencies, "_redis_client", None)
    monkeypatch.setattr(dependencies, "_get_redis_client", lambda: fake_redis)
    return fake_redis


def test_get_current_user_from_bearer_header(jwt_env):
    token = security.create_access_token("a@b.com", ["user"], aud="api")
    request = _make_request(headers={"Authorization": f"Bearer {token}"})
    payload = asyncio.run(dependencies.get_current_user(request))
    assert payload.sub == "a@b.com"
    assert payload.roles == ["user"]


def test_get_current_user_from_cookie(jwt_env):
    token = security.create_access_token("a@b.com", ["user"], aud="api")
    request = _make_request(cookies={"access_token": token})
    payload = asyncio.run(dependencies.get_current_user(request))
    assert payload.sub == "a@b.com"


def test_get_current_user_without_token_raises_401(jwt_env):
    request = _make_request()
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(dependencies.get_current_user(request))
    assert exc_info.value.status_code == 401


def test_get_current_user_rejects_blacklisted_jti(jwt_env, fake_redis):
    token = security.create_access_token("a@b.com", ["user"], aud="api")
    payload = security.verify_token(token, aud="api")

    async def _blacklist():
        await fake_redis.set(f"authgw:blacklist:{payload.jti}", "1")

    asyncio.run(_blacklist())

    request = _make_request(headers={"Authorization": f"Bearer {token}"})
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(dependencies.get_current_user(request))
    assert exc_info.value.status_code == 401


def test_role_checker_allows_matching_role(jwt_env):
    checker = dependencies.RoleChecker("user")
    payload = security.verify_token(
        security.create_access_token("a@b.com", ["user"], aud="api"), aud="api"
    )
    assert checker(payload) is payload


def test_role_checker_rejects_missing_role(jwt_env):
    checker = dependencies.RoleChecker("admin")
    payload = security.verify_token(
        security.create_access_token("a@b.com", ["user"], aud="api"), aud="api"
    )
    with pytest.raises(HTTPException) as exc_info:
        checker(payload)
    assert exc_info.value.status_code == 403
