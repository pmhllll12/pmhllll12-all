"""OAuth 로그인 오케스트레이션 + 리프레시 토큰 로테이션(Redis).

Redis 키 네임스페이스는 `authgw:`로 시작한다 — ontology 크롤러가 이미
`crawler:target:*` 키를 같은 Redis에 쓰고 있어(REDIS_URL 공용) 충돌을 피하려고
이 파일 작성 시점에 임의로 정했다(문서에 구체적 지정 없음).
"""

from __future__ import annotations

import hashlib
import os
from datetime import UTC, datetime, timedelta

import redis.asyncio as redis
from auth.rbac import DEFAULT_ROLES

from core import security
from core.config import AUTHGW_BLACKLIST_PREFIX
from core.matrix import google_oauth_client, kakao_oauth_client, naver_oauth_client
from core.matrix.oauth_state import OAuthNotConfiguredError

__all__ = [
    "ACCESS_TOKEN_EXPIRES_MIN",
    "MOBILE_REFRESH_TOKEN_TTL_SECONDS",
    "MobileSessionNotFoundError",
    "MobileSessionStore",
    "OAuthNotConfiguredError",
    "ProviderNotSupportedError",
    "RefreshReuseDetectedError",
    "RefreshTokenStore",
    "get_mobile_session_store",
    "get_provider_client",
    "issue_mobile_token_pair",
    "issue_token_pair",
]

_REFRESH_KEY_PREFIX = "authgw:refresh:"
_REFRESH_SESSIONS_PREFIX = "authgw:refresh:sessions:"
_BLACKLIST_PREFIX = AUTHGW_BLACKLIST_PREFIX

# 모바일 세션. 웹(`authgw:refresh:*`)과 prefix가 달라 서로의 revoke가 닿지 않는다
# — 한쪽 로그아웃이 다른 쪽에 영향을 주지 않아야 한다는 요구사항이 여기서 지켜진다.
_MOBILE_REFRESH_PREFIX = "authgw:mobile:refresh:"
_MOBILE_SESSIONS_PREFIX = "authgw:mobile:sessions:"

# access token 수명. 웹·모바일 공통이다.
ACCESS_TOKEN_EXPIRES_MIN = 10

# core.security.create_refresh_token의 기본 만료(14일)와 반드시 맞춰야 한다 —
# 여기서만 바꾸면 토큰 만료와 Redis TTL이 어긋난다.
REFRESH_TOKEN_TTL_SECONDS = 14 * 24 * 60 * 60

# 모바일은 웹보다 길게 잡는다 — 앱은 브라우저처럼 세션이 끊기지 않고, 매번 카카오
# 로그인을 다시 하게 만들면 쓸모가 없다. 토큰의 exp와 Redis TTL이 같은 값에서
# 나오도록 issue_mobile_token_pair에서 함께 계산한다.
MOBILE_REFRESH_TOKEN_TTL_DAYS = 30
MOBILE_REFRESH_TOKEN_TTL_SECONDS = MOBILE_REFRESH_TOKEN_TTL_DAYS * 24 * 60 * 60

_PROVIDERS = {
    "google": google_oauth_client,
    "naver": naver_oauth_client,
    "kakao": kakao_oauth_client,
}


class ProviderNotSupportedError(ValueError):
    """`provider`가 google/naver/kakao 중 하나가 아닐 때."""


class RefreshReuseDetectedError(RuntimeError):
    """이미 사용(회전)된 리프레시 토큰이 재사용됐을 때 — 해당 sub의 세션 전체를 폐기한다."""


class MobileSessionNotFoundError(RuntimeError):
    """해당 기기의 모바일 세션이 없을 때(만료·로그아웃 후 갱신 시도)."""


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


def issue_mobile_token_pair(sub: str, aud: str) -> tuple[str, str]:
    """모바일용 토큰 쌍. 리프레시 수명이 길고 access token에 platform 클레임이 붙는다.

    Redis 등록은 별도다 — MobileSessionStore.register.
    """
    access_token = security.create_access_token(sub, DEFAULT_ROLES, aud=aud, platform="mobile")
    refresh_token = security.create_refresh_token(sub, expires_days=MOBILE_REFRESH_TOKEN_TTL_DAYS)
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


def _hash_token(token: str) -> str:
    """리프레시 토큰은 원문이 아니라 해시로만 저장한다 — Redis 덤프가 유출돼도
    그대로 세션을 탈취하지 못하게 한다."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _iso_now() -> str:
    return datetime.now(UTC).isoformat()


class MobileSessionStore:
    """모바일 세션을 **기기 단위**로 관리한다.

    웹은 브라우저가 쿠키를 들고 있어 `jti` 하나면 충분하지만, 모바일은 "이 계정이
    어떤 기기에서 로그인 중인지"를 나열하고 기기별로 끊을 수 있어야 해서
    `{sub}:{device_id}` 복합키 + Hash를 쓴다.

    RefreshTokenStore(웹)를 건드리지 않고 별도 클래스로 두는 이유도 같다 — 두
    저장 구조가 다르고, 한쪽 변경이 다른 쪽 회귀로 번지면 안 된다.
    """

    def __init__(self, redis_url: str | None = None, client: redis.Redis | None = None) -> None:
        self._redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self._client = client

    def _get_client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.from_url(self._redis_url, decode_responses=True)
        return self._client

    @staticmethod
    def _key(sub: str, device_id: str) -> str:
        return f"{_MOBILE_REFRESH_PREFIX}{sub}:{device_id}"

    async def register(
        self,
        sub: str,
        device_id: str,
        refresh_token: str,
        refresh_jti: str,
        ttl_seconds: int,
        kakao_id: str = "",
        device_model: str = "",
    ) -> None:
        """로그인 성공 시 세션을 만든다. 같은 기기로 다시 로그인하면 덮어쓴다 —
        기기 하나당 세션 하나가 원칙이라 재로그인이 세션을 늘리지 않는다."""
        client = self._get_client()
        now = _iso_now()
        key = self._key(sub, device_id)
        await client.hset(
            key,
            mapping={
                "platform": "mobile",
                "refresh_jti": refresh_jti,
                "refresh_hash": _hash_token(refresh_token),
                "device_id": device_id,
                "device_model": device_model,
                "kakao_id": kakao_id,
                "issued_at": now,
                "expires_at": (datetime.now(UTC) + timedelta(seconds=ttl_seconds)).isoformat(),
                "last_active_at": now,
            },
        )
        # TTL은 refresh token 만료와 같은 값이어야 한다. 안 걸면 세션이 영원히 남는다.
        await client.expire(key, ttl_seconds)
        await client.sadd(f"{_MOBILE_SESSIONS_PREFIX}{sub}", device_id)

    async def rotate(
        self,
        sub: str,
        device_id: str,
        old_refresh_token: str,
        new_refresh_token: str,
        new_refresh_jti: str,
        ttl_seconds: int,
    ) -> None:
        """저장된 해시와 대조한 뒤 새 토큰으로 갈아 끼운다.

        해시가 어긋나면 이미 회전된(=탈취 가능성 있는) 토큰이 다시 온 것이므로
        **해당 사용자의 모바일 세션을 전부 폐기**한다. 웹 세션은 건드리지 않는다
        — 웹은 자체 회전 로직이 따로 있고, 플랫폼 격리가 이 설계의 목적이다.
        """
        client = self._get_client()
        key = self._key(sub, device_id)
        stored = await client.hgetall(key)
        if not stored:
            raise MobileSessionNotFoundError(f"모바일 세션이 없습니다 — device_id={device_id!r}")
        if stored.get("refresh_hash") != _hash_token(old_refresh_token):
            await self.revoke_all(sub)
            raise RefreshReuseDetectedError(
                f"리프레시 토큰 재사용 감지 — sub={sub!r}의 모바일 세션을 전부 폐기했습니다."
            )

        now = _iso_now()
        await client.hset(
            key,
            mapping={
                "refresh_jti": new_refresh_jti,
                "refresh_hash": _hash_token(new_refresh_token),
                "issued_at": now,
                "expires_at": (datetime.now(UTC) + timedelta(seconds=ttl_seconds)).isoformat(),
                "last_active_at": now,
            },
        )
        await client.expire(key, ttl_seconds)

    async def revoke(self, sub: str, device_id: str) -> None:
        client = self._get_client()
        await client.delete(self._key(sub, device_id))
        await client.srem(f"{_MOBILE_SESSIONS_PREFIX}{sub}", device_id)

    async def revoke_all(self, sub: str) -> None:
        client = self._get_client()
        session_key = f"{_MOBILE_SESSIONS_PREFIX}{sub}"
        device_ids = await client.smembers(session_key)
        if device_ids:
            await client.delete(*(self._key(sub, device_id) for device_id in device_ids))
        await client.delete(session_key)

    async def list_devices(self, sub: str) -> list[dict]:
        """활성 기기 목록. 세션 Hash에는 TTL이 있지만 인덱스 Set에는 없어서
        만료된 device_id가 남는다 — 조회하면서 같이 청소한다."""
        client = self._get_client()
        session_key = f"{_MOBILE_SESSIONS_PREFIX}{sub}"
        devices: list[dict] = []
        for device_id in await client.smembers(session_key):
            stored = await client.hgetall(self._key(sub, device_id))
            if stored:
                devices.append(stored)
            else:
                await client.srem(session_key, device_id)
        return devices

    async def blacklist_access_token(self, jti: str, ttl_seconds: int) -> None:
        """로그아웃 직후에도 access token은 최대 10분 살아 있다. 즉시 끊으려면
        블랙리스트에 올린다 — 키는 웹과 공유한다(jti가 UUID4라 충돌하지 않고,
        검증부는 토큰이 어느 플랫폼 것인지 모른 채 조회한다)."""
        if ttl_seconds <= 0:
            return
        client = self._get_client()
        await client.set(f"{_BLACKLIST_PREFIX}{jti}", "1", ex=ttl_seconds)


_default_store: RefreshTokenStore | None = None
_default_mobile_store: MobileSessionStore | None = None


def get_refresh_store() -> RefreshTokenStore:
    """FastAPI Depends용 싱글턴 — ONNX 세션처럼 매 요청 재생성하면 Redis 커넥션이
    낭비된다. 테스트는 `app.dependency_overrides[get_refresh_store]`로 교체한다."""
    global _default_store
    if _default_store is None:
        _default_store = RefreshTokenStore()
    return _default_store


def get_mobile_session_store() -> MobileSessionStore:
    """모바일 세션 저장소 싱글턴. 교체 방식은 get_refresh_store와 같다."""
    global _default_mobile_store
    if _default_mobile_store is None:
        _default_mobile_store = MobileSessionStore()
    return _default_mobile_store
