"""RS256 JWT 발급·검증 — auth 게이트웨이(apps/auth)와 백엔드가 공용으로 쓴다.

발급부(create_access_token/create_refresh_token)는 JWT_PRIVATE_KEY가 있는 auth
컨테이너에서만 호출된다. 검증부(verify_token)는 JWT_PUBLIC_KEY만 있으면 모든
컨테이너에서 동작한다 — 백엔드 컨테이너가 이 모듈을 import만 해도 개인키 부재로
에러가 나면 안 되므로, 키는 함수 호출 시점에 읽는다(모듈 로드 시점 X).
"""

from __future__ import annotations

import base64
import binascii
import os
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

__all__ = [
    "COOKIE_KWARGS",
    "TokenPayload",
    "create_access_token",
    "create_refresh_token",
    "get_public_jwk",
    "hash_password",
    "verify_password",
    "verify_token",
]

_ALGORITHM = "RS256"

# auth 발급 쿠키(access_token/refresh_token)에 공통으로 쓰는 옵션.
# domain을 .pmhllll12.cloud로 두면 api./auth. 서브도메인 모두에서 쿠키가 전달된다.
COOKIE_KWARGS = {
    "domain": os.getenv("AUTH_COOKIE_DOMAIN", ".pmhllll12.cloud"),
    "secure": True,
    "httponly": True,
    "samesite": "lax",
}


@dataclass(frozen=True)
class TokenPayload:
    sub: str
    roles: list[str]
    aud: str
    exp: int
    iat: int
    jti: str


def _load_key(env_var: str) -> str:
    """PEM 문자열 또는 base64 인코딩된 PEM을 읽어 PEM 문자열로 반환한다.

    멀티라인 PEM을 .env/GH Actions secret에 그대로 넣기 어려운 환경이 있어
    base64 인코딩도 허용한다(2.7 키 생성 스크립트 참고).
    """
    raw = os.getenv(env_var)
    if not raw:
        raise RuntimeError(f"{env_var} 가 설정되지 않았습니다.")
    raw = raw.strip()
    if raw.startswith("-----BEGIN"):
        return raw
    try:
        decoded = base64.b64decode(raw, validate=True).decode("utf-8")
    except (binascii.Error, ValueError) as exc:
        raise RuntimeError(f"{env_var} 를 PEM 또는 base64(PEM)로 해석할 수 없습니다.") from exc
    if not decoded.startswith("-----BEGIN"):
        raise RuntimeError(f"{env_var} 의 디코딩 결과가 PEM 형식이 아닙니다.")
    return decoded


def _kid() -> str:
    return os.getenv("JWT_KID", "authgw-1")


def create_access_token(
    sub: str, roles: list[str], aud: str, expires_min: int = 10
) -> str:
    private_key = _load_key("JWT_PRIVATE_KEY")
    now = datetime.now(UTC)
    payload = {
        "sub": sub,
        "roles": roles,
        "aud": aud,
        "iat": now,
        "exp": now + timedelta(minutes=expires_min),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(
        payload, private_key, algorithm=_ALGORITHM, headers={"kid": _kid()}
    )


def create_refresh_token(sub: str, expires_days: int = 14) -> str:
    """리프레시 토큰 발급. aud는 항상 'refresh' 고정 — access token과 교차 사용 불가.

    만료 기본값(14일)은 이 저장소에 별도 정책이 없어 임의로 정한 값이다
    — 세션 유지 기간 요구사항이 정해지면 조정한다.
    """
    private_key = _load_key("JWT_PRIVATE_KEY")
    now = datetime.now(UTC)
    payload = {
        "sub": sub,
        "roles": [],
        "aud": "refresh",
        "iat": now,
        "exp": now + timedelta(days=expires_days),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(
        payload, private_key, algorithm=_ALGORITHM, headers={"kid": _kid()}
    )


def verify_token(token: str, aud: str) -> TokenPayload:
    """서명·만료·audience를 검증한다. 허용 알고리즘은 RS256으로 하드코딩되어
    있다 — alg=none/HS256 강제 토큰(키 혼동 공격)을 막기 위해 절대 설정으로
    빼지 않는다."""
    public_key = _load_key("JWT_PUBLIC_KEY")
    payload = jwt.decode(token, public_key, algorithms=["RS256"], audience=aud)
    return TokenPayload(
        sub=payload["sub"],
        roles=payload.get("roles", []),
        aud=payload["aud"],
        exp=payload["exp"],
        iat=payload["iat"],
        jti=payload["jti"],
    )


def hash_password(raw: str) -> str:
    return bcrypt.hashpw(raw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(raw: str, hashed: str) -> bool:
    return bcrypt.checkpw(raw.encode("utf-8"), hashed.encode("utf-8"))


def get_public_jwk() -> dict:
    """공개키를 JWK(RSA) 형식으로 반환 — /.well-known/jwks.json이 그대로 노출."""
    from cryptography.hazmat.primitives.serialization import load_pem_public_key

    public_key = load_pem_public_key(_load_key("JWT_PUBLIC_KEY").encode("utf-8"))
    numbers = public_key.public_numbers()  # type: ignore[union-attr]

    def _b64url_uint(value: int) -> str:
        length = (value.bit_length() + 7) // 8
        return base64.urlsafe_b64encode(value.to_bytes(length, "big")).rstrip(b"=").decode("ascii")

    return {
        "kty": "RSA",
        "use": "sig",
        "alg": _ALGORITHM,
        "kid": _kid(),
        "n": _b64url_uint(numbers.n),
        "e": _b64url_uint(numbers.e),
    }
