"""OAuth 로그인 오케스트레이션 + 리프레시 토큰 로테이션(Redis).

Redis 키 네임스페이스는 `authgw:`로 시작한다 — ontology 크롤러가 이미
`crawler:target:*` 키를 같은 Redis에 쓰고 있어(REDIS_URL 공용) 충돌을 피하려고
이 파일 작성 시점에 임의로 정했다(문서에 구체적 지정 없음).
"""

from __future__ import annotations

import os

import redis.asyncio as redis
from auth.rbac import DEFAULT_ROLES

from core import security
from core.config import AUTHGW_BLACKLIST_PREFIX
from core.matrix import google_oauth_client, kakao_oauth_client, naver_oauth_client
from core.matrix.oauth_state import OAuthNotConfiguredError

__all__ = [
    "OAuthNotConfiguredError",
    "ProviderNotSupportedError",
    "RefreshReuseDetectedError",
    "RefreshTokenStore",
    "get_provider_client",
    "issue_token_pair",
]

_REFRESH_KEY_PREFIX = "authgw:refresh:"
_REFRESH_SESSIONS_PREFIX = "authgw:refresh:sessions:"
_BLACKLIST_PREFIX = AUTHGW_BLACKLIST_PREFIX

# core.security.create_refresh_token의 기본 만료(14일)와 반드시 맞춰야 한다 —
# 여기서만 바꾸면 토큰 만료와 Redis TTL이 어긋난다.
REFRESH_TOKEN_TTL_SECONDS = 14 * 24 * 60 * 60

_PROVIDERS = {
    "google": google_oauth_client,
    "naver": naver_oauth_client,
    "kakao": kakao_oauth_client,
}


class ProviderNotSupportedError(ValueError):
    """`provider`가 google/naver/kakao 중 하나가 아닐 때."""


class RefreshReuseDetectedError(RuntimeError):
    """이미 사용(회전)된 리프레시 토큰이 재사용됐을 때 — 해당 sub의 세션 전체를 폐기한다."""


def get_provider_client(provider: str):
    client = _PROVIDERS.get(provider)
    if client is None:
        raise ProviderNotSupportedError(
            f"지원하지 않는 provider: {provider!r} (google/naver/kakao 중 하나)"
        )
    return client


def issue_token_pair(sub: str, aud: str) -> tuple[str, str]:
    """access_token, refresh_token 튜플을 발급한다(Redis 등록은 별도 —
    RefreshTokenStore.register)."""
    access_token = security.create_access_token(sub, DEFAULT_ROLES, aud=aud)
    refresh_token = security.create_refresh_token(
        sub, expires_days=REFRESH_TOKEN_TTL_SECONDS // 86400
    )
    return access_token, refresh_token


class RefreshTokenStore:
    """리프레시 토큰 회전·재사용 감지·즉시 차단(블랙리스트)을 Redis로 관리한다."""

    def __init__(self, redis_url: str | None = None, client: redis.Redis | None = None) -> None:
        self._redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._client = client

    def _get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(self._redis_url, decode_responses=True)
        return self._client

    async def register(self, sub: str, jti: str, ttl_seconds: int) -> None:
        client = self._get_client()
        await client.set(f"{_REFRESH_KEY_PREFIX}{jti}", sub, ex=ttl_seconds)
        await client.sadd(f"{_REFRESH_SESSIONS_PREFIX}{sub}", jti)

    async def rotate(self, sub: str, old_jti: str) -> None:
        """old_jti가 유효(등록됨)하면 소비하고 넘어간다. 이미 없으면(재사용) 세션
        전체를 폐기하고 예외를 던진다."""
        client = self._get_client()
        stored_sub = await client.get(f"{_REFRESH_KEY_PREFIX}{old_jti}")
        if stored_sub is None or stored_sub != sub:
            await self.revoke_all(sub)
            raise RefreshReuseDetectedError(
                f"리프레시 토큰 재사용 감지 — sub={sub!r}의 세션을 전부 폐기했습니다."
            )
        await client.delete(f"{_REFRESH_KEY_PREFIX}{old_jti}")
        await client.srem(f"{_REFRESH_SESSIONS_PREFIX}{sub}", old_jti)

    async def revoke(self, sub: str, jti: str) -> None:
        client = self._get_client()
        await client.delete(f"{_REFRESH_KEY_PREFIX}{jti}")
        await client.srem(f"{_REFRESH_SESSIONS_PREFIX}{sub}", jti)

    async def revoke_all(self, sub: str) -> None:
        client = self._get_client()
        session_key = f"{_REFRESH_SESSIONS_PREFIX}{sub}"
        jtis = await client.smembers(session_key)
        if jtis:
            await client.delete(*(f"{_REFRESH_KEY_PREFIX}{jti}" for jti in jtis))
        await client.delete(session_key)

    async def blacklist_access_token(self, jti: str, ttl_seconds: int) -> None:
        """access token을 자연 만료 전에 즉시 차단할 때(계정 정지 등) 사용."""
        client = self._get_client()
        await client.set(f"{_BLACKLIST_PREFIX}{jti}", "1", ex=ttl_seconds)

    async def is_access_token_blacklisted(self, jti: str) -> bool:
        client = self._get_client()
        return await client.exists(f"{_BLACKLIST_PREFIX}{jti}") == 1


_default_store: RefreshTokenStore | None = None


def get_refresh_store() -> RefreshTokenStore:
    """FastAPI Depends용 싱글턴 — ONNX 세션처럼 매 요청 재생성하면 Redis 커넥션이
    낭비된다. 테스트는 `app.dependency_overrides[get_refresh_store]`로 교체한다."""
    global _default_store
    if _default_store is None:
        _default_store = RefreshTokenStore()
    return _default_store
