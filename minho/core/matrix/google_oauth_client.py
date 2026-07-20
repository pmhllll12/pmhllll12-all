"""구글 OAuth 로그인 — 인증 URL 생성·code 교환·state 서명을 담당한다."""

from __future__ import annotations

import hashlib
import hmac
import os
from urllib.parse import urlencode

import httpx

_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
_TOKEN_URL = "https://oauth2.googleapis.com/token"
_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

ALLOWED_RETURN_ORIGINS = frozenset(
    {
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://pmhllll12.cloud",
        "https://www.pmhllll12.cloud",
    }
)
DEFAULT_RETURN_ORIGIN = "http://localhost:3000"


class GoogleOAuthNotConfiguredError(RuntimeError):
    """GOOGLE_CLIENT_ID/SECRET/REDIRECT_URI 또는 SESSION_SECRET 이 없을 때."""


def _require_env(name: str) -> str:
    value = (os.getenv(name) or "").strip()
    if not value:
        raise GoogleOAuthNotConfiguredError(
            f"{name} 가 설정되지 않았습니다. backend/.env 를 확인하세요."
        )
    return value


def resolve_return_origin(raw: str | None) -> str:
    """허용 목록에 없는 origin 은 기본값으로 대체한다 (오픈리다이렉트 방지)."""
    candidate = (raw or "").strip().rstrip("/")
    return candidate if candidate in ALLOWED_RETURN_ORIGINS else DEFAULT_RETURN_ORIGIN


def sign_state(return_to: str) -> str:
    secret = _require_env("SESSION_SECRET")
    signature = hmac.new(secret.encode(), return_to.encode(), hashlib.sha256).hexdigest()
    return f"{return_to}.{signature}"


def verify_state(state: str) -> str | None:
    """서명이 유효하면 return_to 를, 아니면 None 을 반환한다."""
    secret = _require_env("SESSION_SECRET")
    return_to, _, signature = state.rpartition(".")
    if not return_to or not signature:
        return None
    expected = hmac.new(secret.encode(), return_to.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        return None
    return return_to


def build_authorize_url(state: str) -> str:
    params = {
        "client_id": _require_env("GOOGLE_CLIENT_ID"),
        "redirect_uri": _require_env("GOOGLE_REDIRECT_URI"),
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "online",
        "prompt": "select_account",
    }
    return f"{_AUTHORIZE_URL}?{urlencode(params)}"


async def exchange_code_for_tokens(code: str) -> dict:
    payload = {
        "client_id": _require_env("GOOGLE_CLIENT_ID"),
        "client_secret": _require_env("GOOGLE_CLIENT_SECRET"),
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": _require_env("GOOGLE_REDIRECT_URI"),
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
