"""카카오 OAuth 로그인 — 인증 URL 생성·code 교환을 담당한다."""

from __future__ import annotations

import os
from urllib.parse import urlencode

import httpx

from core.matrix.oauth_state import require_env

_AUTHORIZE_URL = "https://kauth.kakao.com/oauth/authorize"
_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
_USERINFO_URL = "https://kapi.kakao.com/v2/user/me"


def build_authorize_url(state: str) -> str:
    params = {
        "client_id": require_env("KAKAO_CLIENT_ID"),
        "redirect_uri": require_env("KAKAO_REDIRECT_URI"),
        "response_type": "code",
        "state": state,
    }
    return f"{_AUTHORIZE_URL}?{urlencode(params)}"


async def exchange_code_for_tokens(code: str) -> dict:
    payload = {
        "grant_type": "authorization_code",
        "client_id": require_env("KAKAO_CLIENT_ID"),
        "redirect_uri": require_env("KAKAO_REDIRECT_URI"),
        "code": code,
    }
    # 카카오는 "Client Secret" 기능을 켰을 때만 필요 — 안 켰으면 비워둬도 된다.
    client_secret = (os.getenv("KAKAO_CLIENT_SECRET") or "").strip()
    if client_secret:
        payload["client_secret"] = client_secret

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            _TOKEN_URL,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        return response.json()


async def fetch_userinfo(access_token: str) -> dict:
    """kakao_account.email / properties.nickname 을 꺼내 email/name 으로 정규화."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            _USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"}
        )
        response.raise_for_status()
        body = response.json()

    account = body.get("kakao_account", {})
    properties = body.get("properties", {})
    return {
        "email": account.get("email", ""),
        "name": properties.get("nickname", ""),
    }
