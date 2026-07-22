from __future__ import annotations

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


@pytest.fixture(scope="session")
def rsa_keypair() -> tuple[str, str]:
    """테스트용 RSA 키쌍(PEM 문자열) 한 번만 생성해 세션 내내 재사용한다."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    public_pem = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode("utf-8")
    )
    return private_pem, public_pem


@pytest.fixture()
def jwt_env(monkeypatch: pytest.MonkeyPatch, rsa_keypair: tuple[str, str]) -> tuple[str, str]:
    private_pem, public_pem = rsa_keypair
    monkeypatch.setenv("JWT_PRIVATE_KEY", private_pem)
    monkeypatch.setenv("JWT_PUBLIC_KEY", public_pem)
    monkeypatch.setenv("JWT_KID", "test-kid")
    monkeypatch.setenv("API_AUD", "api")
    monkeypatch.setenv("SESSION_SECRET", "test-session-secret")
    monkeypatch.setenv("AUTH_COOKIE_DOMAIN", ".example.test")
    return private_pem, public_pem


class FakeRedis:
    """RefreshTokenStore/core.dependencies가 쓰는 메서드만 흉내내는 인메모리 더블.

    실제 redis 서버 없이 회전·재사용 감지·블랙리스트 로직을 검증하려고 만들었다
    (이 환경엔 fakeredis 패키지도, 로컬 redis 서버도 없음).
    """

    def __init__(self) -> None:
        self._store: dict[str, str] = {}
        self._sets: dict[str, set[str]] = {}

    async def set(self, key: str, value: str, ex: int | None = None) -> None:  # noqa: ARG002
        self._store[key] = value

    async def get(self, key: str) -> str | None:
        return self._store.get(key)

    async def sadd(self, key: str, *values: str) -> None:
        self._sets.setdefault(key, set()).update(values)

    async def srem(self, key: str, *values: str) -> None:
        self._sets.get(key, set()).difference_update(values)

    async def smembers(self, key: str) -> set[str]:
        return set(self._sets.get(key, set()))

    async def delete(self, *keys: str) -> None:
        for key in keys:
            self._store.pop(key, None)
            self._sets.pop(key, None)

    async def exists(self, key: str) -> int:
        return 1 if key in self._store else 0


@pytest.fixture()
def fake_redis() -> FakeRedis:
    return FakeRedis()
