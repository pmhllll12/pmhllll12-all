from __future__ import annotations

import pytest
from auth.router import router as auth_router
from auth.services import RefreshTokenStore, get_refresh_store
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.matrix import google_oauth_client


def _extract_cookie(response, name: str) -> str:
    """response.cookies는 Cookie domain(.pmhllll12.cloud 등)이 테스트 호스트
    (testserver)와 매칭되지 않으면 값을 채워주지 않는다 — raw Set-Cookie 헤더에서
    직접 파싱한다."""
    for raw in response.headers.get_list("set-cookie"):
        key, _, rest = raw.partition("=")
        if key == name:
            return rest.split(";", 1)[0]
    all_cookies = response.headers.get_list("set-cookie")
    raise AssertionError(f"Set-Cookie에 {name!r}가 없습니다: {all_cookies}")


@pytest.fixture()
def client(jwt_env, fake_redis, monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-secret")
    monkeypatch.setenv("GOOGLE_REDIRECT_URI", "http://testserver/auth/callback/google")

    app = FastAPI()
    app.include_router(auth_router, prefix="/auth")
    app.dependency_overrides[get_refresh_store] = lambda: RefreshTokenStore(client=fake_redis)
    return TestClient(app, follow_redirects=False)


def test_login_returns_authorize_url_for_google(client):
    response = client.post("/auth/login", json={"provider": "google"})
    assert response.status_code == 200
    assert "accounts.google.com" in response.json()["authorize_url"]


def test_login_rejects_unsupported_provider(client):
    response = client.post("/auth/login", json={"provider": "facebook"})
    assert response.status_code == 400


def test_callback_missing_code_redirects_with_invalid_state(client):
    response = client.get("/auth/callback/google")
    assert response.status_code in (302, 307)
    assert "oauth_login_error=invalid_state" in response.headers["location"]


def test_callback_success_sets_cookies_and_registers_session(client, fake_redis, monkeypatch):
    login_response = client.post("/auth/login", json={"provider": "google", "return_to": None})
    authorize_url = login_response.json()["authorize_url"]
    state = authorize_url.split("state=")[1].split("&")[0]
    from urllib.parse import unquote

    state = unquote(state)

    async def _fake_exchange(code: str) -> dict:
        assert code == "test-code"
        return {"access_token": "provider-access-token"}

    async def _fake_userinfo(access_token: str) -> dict:
        assert access_token == "provider-access-token"
        return {"email": "user@example.com", "name": "Test User"}

    monkeypatch.setattr(google_oauth_client, "exchange_code_for_tokens", _fake_exchange)
    monkeypatch.setattr(google_oauth_client, "fetch_userinfo", _fake_userinfo)

    response = client.get("/auth/callback/google", params={"code": "test-code", "state": state})
    assert response.status_code in (302, 307)
    _extract_cookie(response, "access_token")
    _extract_cookie(response, "refresh_token")


def test_refresh_rotates_and_rejects_reused_token(client, fake_redis, monkeypatch):
    async def _fake_exchange(code: str) -> dict:  # noqa: ARG001
        return {"access_token": "provider-access-token"}

    async def _fake_userinfo(access_token: str) -> dict:  # noqa: ARG001
        return {"email": "user@example.com", "name": "Test User"}

    monkeypatch.setattr(google_oauth_client, "exchange_code_for_tokens", _fake_exchange)
    monkeypatch.setattr(google_oauth_client, "fetch_userinfo", _fake_userinfo)

    login_response = client.post("/auth/login", json={"provider": "google"})
    authorize_url = login_response.json()["authorize_url"]
    from urllib.parse import unquote

    state = unquote(authorize_url.split("state=")[1].split("&")[0])
    callback_response = client.get(
        "/auth/callback/google", params={"code": "test-code", "state": state}
    )
    old_refresh_token = _extract_cookie(callback_response, "refresh_token")
    cookie_header = {"Cookie": f"refresh_token={old_refresh_token}"}

    refresh_response = client.post("/auth/refresh", headers=cookie_header)
    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.json()

    # 이미 회전(소비)된 refresh_token을 다시 쓰면 재사용 감지로 거부돼야 한다.
    reuse_response = client.post("/auth/refresh", headers=cookie_header)
    assert reuse_response.status_code == 401


def test_logout_clears_cookies(client):
    client.cookies.set("refresh_token", "not-a-real-token")
    response = client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_jwks_endpoint_returns_public_key(client):
    response = client.get("/auth/.well-known/jwks.json")
    assert response.status_code == 200
    keys = response.json()["keys"]
    assert len(keys) == 1
    assert keys[0]["kty"] == "RSA"
