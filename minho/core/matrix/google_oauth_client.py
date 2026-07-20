"""구글 OAuth 로그인 — 인증 URL 생성·code 교환을 담당한다."""

from __future__ import annotations

from urllib.parse import urlencode

import httpx

from core.matrix.oauth_state import OAuthNotConfiguredError, require_env

__all__ = ["OAuthNotConfiguredError", "build_authorize_url", "exchange_code_for_tokens", "fetch_userinfo"]

_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
_TOKEN_URL = "https://oauth2.googleapis.com/token"
_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def build_authorize_url(state: str) -> str:
    params = {
        "client_id": require_env("GOOGLE_CLIENT_ID"),
        "redirect_uri": require_env("GOOGLE_REDIRECT_URI"),
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "online",
        "prompt": "select_account",
    }
    return f"{_AUTHORIZE_URL}?{urlencode(params)}"


async def exchange_code_for_tokens(code: str) -> dict:
    payload = {
        "client_id": require_env("GOOGLE_CLIENT_ID"),
        "client_secret": require_env("GOOGLE_CLIENT_SECRET"),
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": require_env("GOOGLE_REDIRECT_URI"),
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(_TOKEN_URL, data=payload)
        response.raise_for_status()
        return response.json()


async def fetch_userinfo(access_token: str) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            _USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"}
        )
        response.raise_for_status()
        return response.json()
