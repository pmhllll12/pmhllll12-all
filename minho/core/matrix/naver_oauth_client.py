"""네이버 OAuth 로그인 — 인증 URL 생성·code 교환을 담당한다."""

from __future__ import annotations

from urllib.parse import urlencode

import httpx

from core.matrix.oauth_state import require_env

_AUTHORIZE_URL = "https://nid.naver.com/oauth2.0/authorize"
_TOKEN_URL = "https://nid.naver.com/oauth2.0/token"
_USERINFO_URL = "https://openapi.naver.com/v1/nid/me"


def build_authorize_url(state: str) -> str:
    params = {
        "response_type": "code",
        "client_id": require_env("NAVER_CLIENT_ID"),
        "redirect_uri": require_env("NAVER_REDIRECT_URI"),
        "state": state,
    }
    return f"{_AUTHORIZE_URL}?{urlencode(params)}"


async def exchange_code_for_tokens(code: str, state: str) -> dict:
    params = {
        "grant_type": "authorization_code",
        "client_id": require_env("NAVER_CLIENT_ID"),
        "client_secret": require_env("NAVER_CLIENT_SECRET"),
        "code": code,
        "state": state,
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(_TOKEN_URL, params=params)
        response.raise_for_status()
        return response.json()


async def fetch_userinfo(access_token: str) -> dict:
    """{"resultcode": "00", "response": {"email": ..., "name": ...}} 형태 → response만 반환."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            _USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"}
        )
        response.raise_for_status()
        return response.json().get("response", {})
