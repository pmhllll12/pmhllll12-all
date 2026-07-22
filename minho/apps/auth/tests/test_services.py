from __future__ import annotations

import asyncio

import pytest
from auth.services import RefreshReuseDetectedError, RefreshTokenStore


def test_register_then_rotate_succeeds(fake_redis):
    async def _run():
        store = RefreshTokenStore(client=fake_redis)
        await store.register("a@b.com", "jti-1", ttl_seconds=3600)
        await store.rotate("a@b.com", "jti-1")
        # 회전 후 old jti는 더 이상 유효하지 않다.
        assert await fake_redis.get("authgw:refresh:jti-1") is None

    asyncio.run(_run())


def test_reuse_of_rotated_token_is_detected_and_revokes_all_sessions(fake_redis):
    async def _run():
        store = RefreshTokenStore(client=fake_redis)
        await store.register("a@b.com", "jti-1", ttl_seconds=3600)
        await store.register("a@b.com", "jti-2", ttl_seconds=3600)  # 예: 다른 기기 세션
        await store.rotate("a@b.com", "jti-1")  # 정상 회전 — jti-1 소비됨

        with pytest.raises(RefreshReuseDetectedError):
            await store.rotate("a@b.com", "jti-1")  # 이미 소비된 jti-1 재사용 시도

        # 재사용 감지 시 jti-2(다른 세션)까지 전부 폐기돼야 한다.
        assert await fake_redis.get("authgw:refresh:jti-2") is None

    asyncio.run(_run())


def test_revoke_all_clears_every_session(fake_redis):
    async def _run():
        store = RefreshTokenStore(client=fake_redis)
        await store.register("a@b.com", "jti-1", ttl_seconds=3600)
        await store.register("a@b.com", "jti-2", ttl_seconds=3600)
        await store.revoke_all("a@b.com")
        assert await fake_redis.get("authgw:refresh:jti-1") is None
        assert await fake_redis.get("authgw:refresh:jti-2") is None

    asyncio.run(_run())


def test_blacklist_access_token(fake_redis):
    async def _run():
        store = RefreshTokenStore(client=fake_redis)
        assert not await store.is_access_token_blacklisted("jti-x")
        await store.blacklist_access_token("jti-x", ttl_seconds=60)
        assert await store.is_access_token_blacklisted("jti-x")

    asyncio.run(_run())
