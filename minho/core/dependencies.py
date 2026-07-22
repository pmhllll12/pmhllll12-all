"""백엔드(main.py) 쪽 인증 검증 — apps.auth를 import하지 않는다(auth-isolation).

JWT_PUBLIC_KEY만 있으면 되고, 발급(JWT_PRIVATE_KEY)에는 관여하지 않는다.
"""

from __future__ import annotations

import os

import redis.asyncio as redis
from fastapi import Depends, HTTPException, Request, status

from core.config import API_AUD, AUTHGW_BLACKLIST_PREFIX
from core.security import TokenPayload, verify_token

__all__ = ["RoleChecker", "get_current_user"]

_ACCESS_COOKIE = "access_token"

_redis_client: redis.Redis | None = None


def _get_redis_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        _redis_client = redis.from_url(redis_url, decode_responses=True)
    return _redis_client


def _extract_token(request: Request) -> str | None:
    header = request.headers.get("Authorization")
    if header and header.startswith("Bearer "):
        return header.removeprefix("Bearer ").strip()
    return request.cookies.get(_ACCESS_COOKIE)


async def get_current_user(request: Request) -> TokenPayload:
    token = _extract_token(request)
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="인증 토큰이 없습니다.")

    try:
        payload = verify_token(token, aud=API_AUD)
    except Exception as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 토큰입니다."
        ) from exc

    client = _get_redis_client()
    if await client.exists(f"{AUTHGW_BLACKLIST_PREFIX}{payload.jti}") == 1:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="차단된 토큰입니다.")

    return payload


class RoleChecker:
    def __init__(self, *allowed: str) -> None:
        self._allowed = frozenset(allowed)

    def __call__(self, user: TokenPayload = Depends(get_current_user)) -> TokenPayload:
        if not self._allowed.intersection(user.roles):
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="권한이 없습니다.")
        return user
