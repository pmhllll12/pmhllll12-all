"""모바일 카카오 로그인 라우터.

핵심 검증 대상은 **모바일 세션과 웹 세션의 격리**다 — 한쪽 로그아웃이 다른 쪽에
닿지 않아야 한다는 게 이 설계의 존재 이유이므로, 그걸 증명하지 못하면 나머지
테스트가 통과해도 요구사항을 만족한 게 아니다.
"""

from __future__ import annotations

import httpx
import pytest
from auth.router import router as auth_router
from auth.router_mobile import router as auth_mobile_router
from auth.services import (
    MOBILE_REFRESH_TOKEN_TTL_SECONDS,
    MobileSessionStore,
    RefreshTokenStore,
    get_mobile_session_store,
    get_refresh_store,
)
from fastapi import FastAPI
from fastapi.testclient import TestClient

from core.matrix import kakao_oauth_client

DEVICE_A = "device-aaa"
DEVICE_B = "device-bbb"
EMAIL = "user@example.com"


@pytest.fixture()
def client(jwt_env, fake_redis):
    app = FastAPI()
    app.include_router(auth_router, prefix="/auth")
    app.include_router(auth_mobile_router, prefix="/auth")
    app.dependency_overrides[get_refresh_store] = lambda: RefreshTokenStore(client=fake_redis)
    app.dependency_overrides[get_mobile_session_store] = lambda: MobileSessionStore(
        client=fake_redis
    )
    return TestClient(app)


@pytest.fixture()
def kakao_ok(monkeypatch):
    """카카오 access token 검증이 성공한 것으로 둔다."""

    async def _verify(access_token: str) -> dict:  # noqa: ARG001
        return {"kakao_id": "3123456789", "email": EMAIL, "name": "테스트"}

    monkeypatch.setattr(kakao_oauth_client, "verify_access_token", _verify)


def _login(client, device_id: str = DEVICE_A) -> dict:
    response = client.post(
        "/auth/kakao/mobile",
        json={"access_token": "kakao-access-token"},
        headers={"X-Device-Id": device_id, "X-Device-Model": "SM-N960N"},
    )
    assert response.status_code == 200, response.text
    return response.json()


def _mobile_key(device_id: str) -> str:
    return f"authgw:mobile:refresh:{EMAIL}:{device_id}"


# --- 로그인 ----------------------------------------------------------------


def test_login_issues_token_pair_and_stores_session(client, fake_redis, kakao_ok):
    body = _login(client)

    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 600
    assert body["access_token"] and body["refresh_token"]

    session = fake_redis._hashes[_mobile_key(DEVICE_A)]
    assert session["platform"] == "mobile"
    assert session["kakao_id"] == "3123456789"
    assert session["device_model"] == "SM-N960N"
    # TTL은 refresh token 만료와 같은 값이어야 한다.
    assert fake_redis.expirations[_mobile_key(DEVICE_A)] == MOBILE_REFRESH_TOKEN_TTL_SECONDS


def test_login_stores_hash_not_raw_refresh_token(client, fake_redis, kakao_ok):
    """Redis 덤프가 유출돼도 세션을 그대로 탈취하지 못해야 한다."""
    body = _login(client)

    session = fake_redis._hashes[_mobile_key(DEVICE_A)]
    assert body["refresh_token"] not in session.values()
    assert len(session["refresh_hash"]) == 64  # sha256 hex


def test_login_sets_no_cookie(client, kakao_ok):
    """모바일은 secure storage에 직접 담는다 — 쿠키를 쓰지 않는다."""
    response = client.post(
        "/auth/kakao/mobile",
        json={"access_token": "kakao-access-token"},
        headers={"X-Device-Id": DEVICE_A},
    )
    assert response.status_code == 200
    assert not response.headers.get_list("set-cookie")


def test_login_without_device_id_is_400(client, kakao_ok):
    response = client.post("/auth/kakao/mobile", json={"access_token": "t"})
    assert response.status_code == 400


def test_login_without_any_token_is_400(client, kakao_ok):
    response = client.post("/auth/kakao/mobile", json={}, headers={"X-Device-Id": DEVICE_A})
    assert response.status_code == 400


def test_login_with_invalid_kakao_token_is_401(client, monkeypatch):
    async def _verify(access_token: str) -> dict:  # noqa: ARG001
        raise kakao_oauth_client.KakaoTokenInvalidError("만료된 토큰")

    monkeypatch.setattr(kakao_oauth_client, "verify_access_token", _verify)

    response = client.post(
        "/auth/kakao/mobile",
        json={"access_token": "expired"},
        headers={"X-Device-Id": DEVICE_A},
    )
    assert response.status_code == 401


def test_login_without_email_consent_is_403(client, monkeypatch):
    async def _verify(access_token: str) -> dict:  # noqa: ARG001
        return {"kakao_id": "3123456789", "email": "", "name": "테스트"}

    monkeypatch.setattr(kakao_oauth_client, "verify_access_token", _verify)

    response = client.post(
        "/auth/kakao/mobile",
        json={"access_token": "t"},
        headers={"X-Device-Id": DEVICE_A},
    )
    assert response.status_code == 403


def test_login_when_kakao_api_fails_is_502(client, monkeypatch):
    async def _verify(access_token: str) -> dict:  # noqa: ARG001
        raise httpx.ConnectError("카카오 접속 불가")

    monkeypatch.setattr(kakao_oauth_client, "verify_access_token", _verify)

    response = client.post(
        "/auth/kakao/mobile",
        json={"access_token": "t"},
        headers={"X-Device-Id": DEVICE_A},
    )
    assert response.status_code == 502


def test_login_prefers_id_token_when_configured(client, monkeypatch):
    """OIDC를 켠 앱은 카카오 API 왕복 없이 로컬 검증으로 끝나야 한다."""
    called: list[str] = []

    async def _verify_id(id_token: str) -> dict:
        called.append(id_token)
        return {"kakao_id": "3123456789", "email": EMAIL, "name": "테스트"}

    async def _verify_access(access_token: str) -> dict:  # noqa: ARG001
        raise AssertionError("id_token이 있으면 access_token 경로를 타면 안 된다")

    monkeypatch.setattr(kakao_oauth_client, "verify_id_token", _verify_id)
    monkeypatch.setattr(kakao_oauth_client, "verify_access_token", _verify_access)

    response = client.post(
        "/auth/kakao/mobile",
        json={"access_token": "a", "id_token": "i"},
        headers={"X-Device-Id": DEVICE_A},
    )
    assert response.status_code == 200
    assert called == ["i"]


def test_login_falls_back_to_access_token_when_oidc_not_configured(client, monkeypatch):
    """서버에 KAKAO_NATIVE_APP_KEY가 없어도 앱을 다시 배포하지 않아도 되게 한다."""
    from core.matrix.oauth_state import OAuthNotConfiguredError

    async def _verify_id(id_token: str) -> dict:  # noqa: ARG001
        raise OAuthNotConfiguredError("KAKAO_NATIVE_APP_KEY 없음")

    async def _verify_access(access_token: str) -> dict:  # noqa: ARG001
        return {"kakao_id": "3123456789", "email": EMAIL, "name": "테스트"}

    monkeypatch.setattr(kakao_oauth_client, "verify_id_token", _verify_id)
    monkeypatch.setattr(kakao_oauth_client, "verify_access_token", _verify_access)

    response = client.post(
        "/auth/kakao/mobile",
        json={"access_token": "a", "id_token": "i"},
        headers={"X-Device-Id": DEVICE_A},
    )
    assert response.status_code == 200


# --- 갱신 ------------------------------------------------------------------


def test_refresh_rotates_and_rejects_reused_token(client, kakao_ok):
    tokens = _login(client)
    headers = {"X-Device-Id": DEVICE_A}

    first = client.post(
        "/auth/mobile/refresh",
        json={"refresh_token": tokens["refresh_token"]},
        headers=headers,
    )
    assert first.status_code == 200
    assert first.json()["refresh_token"] != tokens["refresh_token"]

    # 회전된 옛 토큰을 다시 쓰면 탈취로 간주해 거부한다.
    reuse = client.post(
        "/auth/mobile/refresh",
        json={"refresh_token": tokens["refresh_token"]},
        headers=headers,
    )
    assert reuse.status_code == 401


def test_refresh_reuse_revokes_only_mobile_sessions_of_that_user(client, fake_redis, kakao_ok):
    tokens = _login(client, DEVICE_A)
    _login(client, DEVICE_B)
    fake_redis._store["authgw:refresh:web-jti"] = EMAIL  # 웹 세션이 살아 있는 상태

    client.post(
        "/auth/mobile/refresh",
        json={"refresh_token": tokens["refresh_token"]},
        headers={"X-Device-Id": DEVICE_A},
    )
    reuse = client.post(
        "/auth/mobile/refresh",
        json={"refresh_token": tokens["refresh_token"]},
        headers={"X-Device-Id": DEVICE_A},
    )
    assert reuse.status_code == 401

    # 재사용 감지는 그 사용자의 모바일 세션 전체를 끊되, 웹은 남긴다.
    assert _mobile_key(DEVICE_A) not in fake_redis._hashes
    assert _mobile_key(DEVICE_B) not in fake_redis._hashes
    assert fake_redis._store["authgw:refresh:web-jti"] == EMAIL


def test_refresh_without_session_is_401(client, kakao_ok):
    tokens = _login(client, DEVICE_A)
    # 세션을 만든 적 없는 기기로 갱신을 시도한다.
    response = client.post(
        "/auth/mobile/refresh",
        json={"refresh_token": tokens["refresh_token"]},
        headers={"X-Device-Id": "unknown-device"},
    )
    assert response.status_code == 401


def test_refresh_without_device_id_is_400(client, kakao_ok):
    tokens = _login(client)
    response = client.post("/auth/mobile/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert response.status_code == 400


# --- 로그아웃 ---------------------------------------------------------------


def test_logout_removes_only_that_device(client, fake_redis, kakao_ok):
    tokens_a = _login(client, DEVICE_A)
    _login(client, DEVICE_B)

    response = client.post(
        "/auth/mobile/logout",
        headers={
            "X-Device-Id": DEVICE_A,
            "Authorization": f"Bearer {tokens_a['access_token']}",
        },
    )
    assert response.status_code == 200
    assert _mobile_key(DEVICE_A) not in fake_redis._hashes
    assert _mobile_key(DEVICE_B) in fake_redis._hashes


def test_logout_blacklists_access_token(client, fake_redis, kakao_ok):
    tokens = _login(client)
    client.post(
        "/auth/mobile/logout",
        headers={
            "X-Device-Id": DEVICE_A,
            "Authorization": f"Bearer {tokens['access_token']}",
        },
    )
    assert any(k.startswith("authgw:blacklist:") for k in fake_redis._store)


def test_logout_requires_bearer_token(client, kakao_ok):
    _login(client)
    response = client.post("/auth/mobile/logout", headers={"X-Device-Id": DEVICE_A})
    assert response.status_code == 401


def test_logout_all_removes_every_mobile_device(client, fake_redis, kakao_ok):
    tokens_a = _login(client, DEVICE_A)
    _login(client, DEVICE_B)

    response = client.post(
        "/auth/mobile/logout-all",
        headers={
            "X-Device-Id": DEVICE_A,
            "Authorization": f"Bearer {tokens_a['access_token']}",
        },
    )
    assert response.status_code == 200
    assert _mobile_key(DEVICE_A) not in fake_redis._hashes
    assert _mobile_key(DEVICE_B) not in fake_redis._hashes


# --- 플랫폼 격리 (이 설계의 존재 이유) --------------------------------------


def test_mobile_logout_all_leaves_web_session_intact(client, fake_redis, kakao_ok):
    tokens = _login(client)
    fake_redis._store["authgw:refresh:web-jti"] = EMAIL
    await_sets = fake_redis._sets.setdefault(f"authgw:refresh:sessions:{EMAIL}", set())
    await_sets.add("web-jti")

    client.post(
        "/auth/mobile/logout-all",
        headers={
            "X-Device-Id": DEVICE_A,
            "Authorization": f"Bearer {tokens['access_token']}",
        },
    )

    assert fake_redis._store["authgw:refresh:web-jti"] == EMAIL
    assert "web-jti" in fake_redis._sets[f"authgw:refresh:sessions:{EMAIL}"]


def test_web_logout_leaves_mobile_session_intact(client, fake_redis, kakao_ok):
    tokens = _login(client)
    web_refresh = _issue_web_refresh_and_register(fake_redis)

    response = client.post("/auth/logout", headers={"Cookie": f"refresh_token={web_refresh}"})
    assert response.status_code == 200

    # 웹 로그아웃이 모바일 세션을 건드리지 않았다.
    session = fake_redis._hashes[_mobile_key(DEVICE_A)]
    assert session["platform"] == "mobile"
    assert tokens["refresh_token"] not in session.values()


def _issue_web_refresh_and_register(fake_redis) -> str:
    """웹 흐름이 만들어 둔 세션을 흉내낸다(카카오 콜백 전체를 태우지 않고)."""
    import asyncio

    from core import security

    token = security.create_refresh_token(EMAIL)
    payload = security.verify_token(token, aud="refresh")
    store = RefreshTokenStore(client=fake_redis)
    asyncio.run(store.register(EMAIL, payload.jti, 3600))
    return token


def test_access_token_carries_platform_claim(client, kakao_ok):
    """모바일 토큰으로 웹 전용 경로를 부르는 것을 구분할 수 있어야 한다."""
    from core import security

    tokens = _login(client)
    payload = security.verify_token(tokens["access_token"], aud="api")
    assert payload.platform == "mobile"
