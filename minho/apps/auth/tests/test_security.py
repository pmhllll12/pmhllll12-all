from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt
import pytest

from core import security


def test_access_token_roundtrip(jwt_env):
    token = security.create_access_token("a@b.com", ["user"], aud="api")
    payload = security.verify_token(token, aud="api")
    assert payload.sub == "a@b.com"
    assert payload.roles == ["user"]
    assert payload.aud == "api"


def test_refresh_token_has_refresh_audience(jwt_env):
    token = security.create_refresh_token("a@b.com")
    payload = security.verify_token(token, aud="refresh")
    assert payload.aud == "refresh"
    assert payload.roles == []


def test_access_and_refresh_audiences_are_not_interchangeable(jwt_env):
    access_token = security.create_access_token("a@b.com", ["user"], aud="api")
    with pytest.raises(jwt.InvalidAudienceError):
        security.verify_token(access_token, aud="refresh")

    refresh_token = security.create_refresh_token("a@b.com")
    with pytest.raises(jwt.InvalidAudienceError):
        security.verify_token(refresh_token, aud="api")


def test_wrong_audience_rejected(jwt_env):
    token = security.create_access_token("a@b.com", ["user"], aud="api")
    with pytest.raises(jwt.InvalidAudienceError):
        security.verify_token(token, aud="some-other-service")


def test_expired_token_rejected(jwt_env):
    token = security.create_access_token("a@b.com", ["user"], aud="api", expires_min=-1)
    with pytest.raises(jwt.ExpiredSignatureError):
        security.verify_token(token, aud="api")


def test_tampered_signature_rejected(jwt_env):
    token = security.create_access_token("a@b.com", ["user"], aud="api")
    header, payload, signature = token.split(".")
    tampered = f"{header}.{payload}.{signature[:-4]}zzzz"
    with pytest.raises(jwt.InvalidSignatureError):
        security.verify_token(tampered, aud="api")


def test_alg_none_forged_token_rejected(jwt_env):
    """alg=none으로 서명 없이 만든 토큰 — verify_token이 algorithms=["RS256"]로
    하드코딩돼 있어 거부돼야 한다(설정으로 뺐다면 이 공격이 통과할 수 있음)."""
    now = datetime.now(UTC)
    forged = jwt.encode(
        {
            "sub": "attacker@evil.com",
            "roles": ["admin"],
            "aud": "api",
            "iat": now,
            "exp": now + timedelta(minutes=10),
            "jti": "forged",
        },
        key="",
        algorithm="none",
    )
    with pytest.raises(jwt.InvalidAlgorithmError):
        security.verify_token(forged, aud="api")


def test_hs256_forged_token_using_public_key_as_secret_rejected(jwt_env):
    """공개키를 HMAC 비밀키로 재사용하는 '키 혼동(key confusion)' 공격 시도.

    PyJWT의 encode()는 PEM처럼 보이는 문자열을 HMAC 비밀키로 쓰면 자체적으로
    거부한다(InvalidKeyError) — 그래서 여기서는 그 가드를 우회해 raw HMAC-SHA256
    서명으로 직접 토큰을 조립해, verify_token의 algorithms=["RS256"] 하드코딩이
    실제로 이 공격을 막는지 검증한다.
    """
    import base64
    import hashlib
    import hmac as hmac_lib
    import json

    _, public_pem = jwt_env
    now = datetime.now(UTC)

    def _b64url(data: bytes) -> bytes:
        return base64.urlsafe_b64encode(data).rstrip(b"=")

    header = _b64url(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64url(
        json.dumps(
            {
                "sub": "attacker@evil.com",
                "roles": ["admin"],
                "aud": "api",
                "iat": int(now.timestamp()),
                "exp": int((now + timedelta(minutes=10)).timestamp()),
                "jti": "forged",
            }
        ).encode()
    )
    signing_input = header + b"." + payload
    signature = _b64url(
        hmac_lib.new(public_pem.encode("utf-8"), signing_input, hashlib.sha256).digest()
    )
    forged = (signing_input + b"." + signature).decode("ascii")

    with pytest.raises(jwt.InvalidAlgorithmError):
        security.verify_token(forged, aud="api")


def test_password_hash_roundtrip():
    hashed = security.hash_password("hunter2")
    assert security.verify_password("hunter2", hashed)
    assert not security.verify_password("wrong", hashed)


def test_get_public_jwk_shape(jwt_env):
    jwk = security.get_public_jwk()
    assert jwk["kty"] == "RSA"
    assert jwk["alg"] == "RS256"
    assert jwk["kid"] == "test-kid"
    assert "n" in jwk and "e" in jwk


def test_private_key_env_var_not_required_to_import_module(monkeypatch):
    """모듈 로드 시점이 아니라 호출 시점에 키를 읽는다 — import만으로는
    JWT_PRIVATE_KEY 부재 에러가 나면 안 된다(백엔드 컨테이너 요구사항)."""
    monkeypatch.delenv("JWT_PRIVATE_KEY", raising=False)
    monkeypatch.delenv("JWT_PUBLIC_KEY", raising=False)
    import importlib

    importlib.reload(security)  # 재로드해도 에러 없어야 함
    with pytest.raises(RuntimeError):
        security.create_access_token("a@b.com", ["user"], aud="api")
