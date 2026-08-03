"""모바일(Flutter) 카카오 로그인 — 웹 흐름(`router.py`)과 파일부터 분리한다.

웹과 모바일은 세션 수명·토큰 탈취 위험·디바이스 개념이 달라 만료·폐기 정책을
독립적으로 운영해야 한다. 같은 파일에 두면 로직이 섞여 한쪽 수정이 다른 쪽
회귀가 된다.

공유하는 것은 **카카오 토큰 검증**뿐이고(`core.matrix.kakao_oauth_client`),
세션 저장은 `MobileSessionStore`가 `authgw:mobile:*` 네임스페이스에서 따로 한다.

명세 ---> `minho/_docs/flutter-kakao-oauth-harmess.md`
클라이언트 ---> `pmh_flutter/pmh_flutter_application_1/lib/auth.dart`
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Annotated

import httpx
from auth.schemas import (
    KakaoMobileLoginRequest,
    MobileRefreshRequest,
    MobileTokenResponse,
)
from auth.services import (
    ACCESS_TOKEN_EXPIRES_MIN,
    MOBILE_REFRESH_TOKEN_TTL_SECONDS,
    MobileSessionNotFoundError,
    MobileSessionStore,
    RefreshReuseDetectedError,
    get_mobile_session_store,
    issue_mobile_token_pair,
)
from fastapi import APIRouter, Depends, Header, HTTPException, status

from core import security
from core.config import API_AUD
from core.matrix import kakao_oauth_client
from core.matrix.kakao_oauth_client import KakaoTokenInvalidError
from core.matrix.oauth_state import OAuthNotConfiguredError

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth-mobile"])


async def _require_device_id(
    x_device_id: Annotated[str | None, Header(alias="X-Device-Id")] = None,
) -> str:
    """세션 키가 `{sub}:{device_id}`라 기기 식별자 없이는 세션을 만들 수도 찾을
    수도 없다. 그래서 401이 아니라 **400**이다 — 자격증명 문제가 아니라 요청이
    성립하지 않는다."""
    if not x_device_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="X-Device-Id 헤더가 필요합니다.")
    return x_device_id


DeviceId = Annotated[str, Depends(_require_device_id)]
Store = Annotated[MobileSessionStore, Depends(get_mobile_session_store)]


def _bearer_subject(authorization: str | None) -> security.TokenPayload:
    """Authorization 헤더의 access token을 검증해 payload를 돌려준다."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Authorization 헤더가 필요합니다.")
    token = authorization.split(" ", 1)[1].strip()
    try:
        return security.verify_token(token, aud=API_AUD)
    except Exception as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 access token"
        ) from exc


async def _verify_kakao(body: KakaoMobileLoginRequest) -> dict:
    """id_token이 오고 서버도 OIDC 설정을 갖췄으면 로컬 검증(네트워크 0회),
    아니면 access token을 카카오에 물어본다.

    앱이 둘 다 보내도 되도록 만든 이유는 OIDC 사용 여부가 카카오 콘솔 설정에
    달려 있어서다 — 서버가 한쪽을 강제하면 콘솔 설정을 바꿀 때 앱도 같이
    배포해야 한다.
    """
    if body.id_token:
        try:
            return await kakao_oauth_client.verify_id_token(body.id_token)
        except OAuthNotConfiguredError as exc:
            if not body.access_token:
                raise
            logger.info("[mobile] id_token 검증 불가(%s) — access_token으로 진행합니다.", exc)

    if not body.access_token:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="access_token 또는 id_token 중 하나가 필요합니다.",
        )
    return await kakao_oauth_client.verify_access_token(body.access_token)


@router.post("/kakao/mobile", response_model=MobileTokenResponse)
async def kakao_mobile_login(
    body: KakaoMobileLoginRequest,
    device_id: DeviceId,
    store: Store,
    x_device_model: Annotated[str | None, Header(alias="X-Device-Model")] = None,
) -> MobileTokenResponse:
    """카카오 토큰을 검증하고 자체 JWT 쌍을 발급한다.

    쿠키는 설정하지 않는다 — 모바일은 secure storage에 직접 담는다.
    """
    try:
        userinfo = await _verify_kakao(body)
    except KakaoTokenInvalidError as exc:
        logger.info("[mobile] 카카오 토큰 검증 실패: %s", exc)
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="카카오 토큰이 유효하지 않습니다."
        ) from exc
    except OAuthNotConfiguredError as exc:
        logger.warning("[mobile] 카카오 설정 누락: %s", exc)
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except httpx.HTTPError as exc:
        logger.warning("[mobile] 카카오 API 호출 실패: %s", exc)
        raise HTTPException(
            status.HTTP_502_BAD_GATEWAY, detail="카카오 서버와 통신할 수 없습니다."
        ) from exc

    # sub가 이메일이라(웹 흐름과 동일) 이메일 동의가 없으면 세션을 만들 수 없다.
    email = userinfo.get("email", "")
    if not email:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, detail="이메일 제공에 동의해야 가입할 수 있습니다."
        )

    access_token, refresh_token = issue_mobile_token_pair(email, aud=API_AUD)
    refresh_payload = security.verify_token(refresh_token, aud="refresh")
    await store.register(
        sub=email,
        device_id=device_id,
        refresh_token=refresh_token,
        refresh_jti=refresh_payload.jti,
        ttl_seconds=MOBILE_REFRESH_TOKEN_TTL_SECONDS,
        kakao_id=userinfo.get("kakao_id", ""),
        device_model=x_device_model or "",
    )

    return MobileTokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRES_MIN * 60,
    )


@router.post("/mobile/refresh", response_model=MobileTokenResponse)
async def mobile_refresh(
    body: MobileRefreshRequest,
    device_id: DeviceId,
    store: Store,
) -> MobileTokenResponse:
    """리프레시 토큰을 회전시킨다. 응답의 새 refresh_token으로 반드시 덮어써야
    한다 — 옛 토큰을 다시 보내면 재사용으로 간주해 세션을 폐기한다."""
    try:
        payload = security.verify_token(body.refresh_token, aud="refresh")
    except Exception as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 refresh_token"
        ) from exc

    access_token, new_refresh_token = issue_mobile_token_pair(payload.sub, aud=API_AUD)
    new_refresh_payload = security.verify_token(new_refresh_token, aud="refresh")

    try:
        await store.rotate(
            sub=payload.sub,
            device_id=device_id,
            old_refresh_token=body.refresh_token,
            new_refresh_token=new_refresh_token,
            new_refresh_jti=new_refresh_payload.jti,
            ttl_seconds=MOBILE_REFRESH_TOKEN_TTL_SECONDS,
        )
    except (RefreshReuseDetectedError, MobileSessionNotFoundError) as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    return MobileTokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRES_MIN * 60,
    )


@router.post("/mobile/logout")
async def mobile_logout(
    device_id: DeviceId,
    store: Store,
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, bool]:
    """이 기기의 세션만 지운다. 다른 기기와 웹 세션은 그대로 남는다."""
    payload = _bearer_subject(authorization)
    await store.revoke(payload.sub, device_id)
    await _blacklist(store, payload)
    return {"ok": True}


@router.post("/mobile/logout-all")
async def mobile_logout_all(
    device_id: DeviceId,  # noqa: ARG001 — 헤더 규약을 모든 모바일 경로에서 동일하게 유지한다
    store: Store,
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, bool]:
    """이 계정의 **모바일** 세션을 전부 지운다. `authgw:refresh:*`(웹)는
    건드리지 않는다 — 플랫폼 격리가 이 설계의 목적이다."""
    payload = _bearer_subject(authorization)
    await store.revoke_all(payload.sub)
    await _blacklist(store, payload)
    return {"ok": True}


async def _blacklist(store: MobileSessionStore, payload: security.TokenPayload) -> None:
    """로그아웃해도 access token은 남은 수명(최대 10분)만큼 유효하다 — 즉시 끊는다."""
    remaining = payload.exp - int(datetime.now(UTC).timestamp())
    await store.blacklist_access_token(payload.jti, remaining)
