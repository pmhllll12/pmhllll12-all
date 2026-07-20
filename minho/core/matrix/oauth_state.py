"""소셜 로그인 공통 — return_to 검증과 state 서명/검증 (구글/네이버/카카오 공용)."""

from __future__ import annotations

import hashlib
import hmac
import os

ALLOWED_RETURN_ORIGINS = frozenset(
    {
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://pmhllll12.cloud",
        "https://www.pmhllll12.cloud",
    }
)
DEFAULT_RETURN_ORIGIN = "http://localhost:3000"


class OAuthNotConfiguredError(RuntimeError):
    """소셜 로그인에 필요한 환경변수(CLIENT_ID/SECRET/REDIRECT_URI, SESSION_SECRET)가 없을 때."""


def require_env(name: str) -> str:
    value = (os.getenv(name) or "").strip()
    if not value:
        raise OAuthNotConfiguredError(f"{name} 가 설정되지 않았습니다. backend/.env 를 확인하세요.")
    return value


def resolve_return_origin(raw: str | None) -> str:
    """허용 목록에 없는 origin 은 기본값으로 대체한다 (오픈리다이렉트 방지)."""
    candidate = (raw or "").strip().rstrip("/")
    return candidate if candidate in ALLOWED_RETURN_ORIGINS else DEFAULT_RETURN_ORIGIN


def sign_state(return_to: str) -> str:
    secret = require_env("SESSION_SECRET")
    signature = hmac.new(secret.encode(), return_to.encode(), hashlib.sha256).hexdigest()
    return f"{return_to}.{signature}"


def verify_state(state: str) -> str | None:
    """서명이 유효하면 return_to 를, 아니면 None 을 반환한다."""
    secret = require_env("SESSION_SECRET")
    return_to, _, signature = state.rpartition(".")
    if not return_to or not signature:
        return None
    expected = hmac.new(secret.encode(), return_to.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        return None
    return return_to
