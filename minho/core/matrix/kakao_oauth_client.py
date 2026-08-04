"""카카오 OAuth 로그인.

두 가지 흐름을 함께 담는다.

- **웹(code 흐름)** — `build_authorize_url` → `exchange_code_for_tokens` →
  `fetch_userinfo`. 브라우저가 카카오로 갔다 오며 authorization code를 받아온다.
- **모바일(토큰 검증)** — `verify_access_token` / `verify_id_token`. Flutter의
  카카오 SDK가 이미 토큰을 갖고 있어 **code 교환 단계가 없다.** 백엔드는 받은
  토큰이 진짜인지만 확인한다.

모바일 함수만 카카오 회원번호(`kakao_id`)를 돌려준다 — 모바일 세션 해시에
필요하다. 웹 콜백이 의존하는 `fetch_userinfo`의 반환 형태는 건드리지 않았다.
"""

from __future__ import annotations

import asyncio
import os
from functools import lru_cache
from urllib.parse import urlencode

import httpx
import jwt

from core.matrix.oauth_state import OAuthNotConfiguredError, require_env

_AUTHORIZE_URL = "https://kauth.kakao.com/oauth/authorize"
_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
_USERINFO_URL = "https://kapi.kakao.com/v2/user/me"

_ISSUER = "https://kauth.kakao.com"
_JWKS_URL = f"{_ISSUER}/.well-known/jwks.json"


class KakaoTokenInvalidError(ValueError):
    """카카오가 발급하지 않았거나 만료된 토큰. 라우터는 401로 옮긴다."""


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


# ---------------------------------------------------------------------------
# 모바일 — 앱이 이미 들고 있는 토큰을 검증한다
# ---------------------------------------------------------------------------


async def verify_access_token(access_token: str) -> dict:
    """카카오 access token을 `/v2/user/me` 로 검증하고 사용자 정보를 정규화한다.

    401이면 카카오가 발급하지 않았거나 만료된 토큰이다. 그 밖의 실패(네트워크,
    카카오 장애)는 httpx 예외 그대로 올려 보낸다 — 라우터가 502로 옮긴다.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            _USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"}
        )
    if response.status_code == 401:
        raise KakaoTokenInvalidError("카카오 access token이 유효하지 않습니다.")
    response.raise_for_status()

    return _normalize(response.json())


async def verify_id_token(id_token: str) -> dict:
    """카카오 OIDC id_token을 JWKS로 **로컬 검증**한다.

    카카오 API를 부르지 않으므로 access token 경로보다 빠르고 카카오 장애에 덜
    묶인다. 대신 앱 설정에서 OpenID Connect를 켜야 하고, `aud`에 들어가는 앱 키
    (Flutter 네이티브 로그인이면 **네이티브 앱키**)를 백엔드가 알아야 한다.

    `KAKAO_NATIVE_APP_KEY`가 없으면 [OAuthNotConfiguredError] — 라우터는 이때
    access token 경로로 되돌아간다. 어느 쪽을 쓸지는 카카오 콘솔 설정에 달려
    있어 서버가 한쪽을 강제하지 않는다.
    """
    audience = (os.getenv("KAKAO_NATIVE_APP_KEY") or "").strip()
    if not audience:
        raise OAuthNotConfiguredError("KAKAO_NATIVE_APP_KEY 가 없어 id_token을 검증할 수 없습니다.")

    # PyJWKClient는 동기 HTTP를 쓴다. 이벤트 루프를 막지 않도록 스레드로 넘긴다
    # (키는 클라이언트 내부에서 캐시돼 매 요청 네트워크를 타지 않는다).
    signing_key = await asyncio.to_thread(_jwks_client().get_signing_key_from_jwt, id_token)
    try:
        claims = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=audience,
            issuer=_ISSUER,
        )
    except jwt.InvalidTokenError as exc:
        raise KakaoTokenInvalidError(f"카카오 id_token 검증 실패: {exc}") from exc

    # id_token의 sub가 카카오 회원번호다. 이메일·닉네임은 동의 항목에 따라 없을
    # 수 있어 access token 응답과 같은 키로 맞춰 둔다.
    return {
        "kakao_id": str(claims.get("sub", "")),
        "email": claims.get("email", ""),
        "name": claims.get("nickname", ""),
    }


def _normalize(body: dict) -> dict:
    account = body.get("kakao_account", {})
    properties = body.get("properties", {})
    return {
        "kakao_id": str(body.get("id", "")),
        "email": account.get("email", ""),
        "name": properties.get("nickname", ""),
    }


@lru_cache(maxsize=1)
def _jwks_client() -> jwt.PyJWKClient:
    """카카오 공개키 조회 클라이언트. 프로세스당 하나만 두어 키 캐시를 공유한다."""
    return jwt.PyJWKClient(_JWKS_URL)
