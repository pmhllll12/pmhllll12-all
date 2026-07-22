from __future__ import annotations

import logging

from auth.schemas import LoginRequest, RefreshRequest, TokenResponse
from auth.services import (
    REFRESH_TOKEN_TTL_SECONDS,
    ProviderNotSupportedError,
    RefreshReuseDetectedError,
    RefreshTokenStore,
    get_provider_client,
    get_refresh_store,
    issue_token_pair,
)
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse

from core import security
from core.config import API_AUD
from core.matrix.oauth_state import (
    OAuthNotConfiguredError,
    resolve_return_origin,
    sign_state,
    verify_state,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])

_ACCESS_COOKIE = "access_token"
_REFRESH_COOKIE = "refresh_token"
_ACCESS_TOKEN_EXPIRES_MIN = 10


def _set_token_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        _ACCESS_COOKIE,
        access_token,
        max_age=_ACCESS_TOKEN_EXPIRES_MIN * 60,
        **security.COOKIE_KWARGS,
    )
    response.set_cookie(
        _REFRESH_COOKIE, refresh_token, max_age=REFRESH_TOKEN_TTL_SECONDS, **security.COOKIE_KWARGS
    )


def _clear_token_cookies(response: Response) -> None:
    cookie_kwargs = {k: v for k, v in security.COOKIE_KWARGS.items() if k != "httponly"}
    response.delete_cookie(_ACCESS_COOKIE, **cookie_kwargs)
    response.delete_cookie(_REFRESH_COOKIE, **cookie_kwargs)


@router.post("/login")
async def login(body: LoginRequest) -> dict[str, str]:
    """OAuth 인증 URL을 발급한다 — 프런트엔드가 이 URL로 사용자를 이동시킨다."""
    try:
        client = get_provider_client(body.provider)
    except ProviderNotSupportedError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    origin = resolve_return_origin(body.return_to)
    try:
        state = sign_state(origin)
    except OAuthNotConfiguredError as exc:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    return {"authorize_url": client.build_authorize_url(state)}


@router.get("/callback/{provider}")
async def callback(
    provider: str,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    store: RefreshTokenStore = Depends(get_refresh_store),
) -> RedirectResponse:
    try:
        client = get_provider_client(provider)
    except ProviderNotSupportedError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    origin = resolve_return_origin(None)
    if state:
        verified_origin = verify_state(state)
        if verified_origin:
            origin = verified_origin

    if error:
        logger.info("[/auth/callback/%s] 인증 거부/취소 — error=%s", provider, error)
        return RedirectResponse(f"{origin}?oauth_login_error={error}")
    if not code or not state or not verify_state(state):
        return RedirectResponse(f"{origin}?oauth_login_error=invalid_state")

    try:
        tokens = await client.exchange_code_for_tokens(code)
        userinfo = await client.fetch_userinfo(tokens["access_token"])
    except OAuthNotConfiguredError as exc:
        logger.warning("[/auth/callback/%s] %s", provider, exc)
        return RedirectResponse(f"{origin}?oauth_login_error=not_configured")
    except Exception:
        logger.exception("[/auth/callback/%s] 토큰 교환/사용자 정보 조회 실패", provider)
        return RedirectResponse(f"{origin}?oauth_login_error=oauth_failed")

    email = userinfo.get("email", "")
    if not email:
        return RedirectResponse(f"{origin}?oauth_login_error=no_email")

    access_token, refresh_token = issue_token_pair(email, aud=API_AUD)
    refresh_payload = security.verify_token(refresh_token, aud="refresh")
    await store.register(email, refresh_payload.jti, REFRESH_TOKEN_TTL_SECONDS)

    response = RedirectResponse(origin)
    _set_token_cookies(response, access_token, refresh_token)
    return response


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request,
    body: RefreshRequest | None = None,
    store: RefreshTokenStore = Depends(get_refresh_store),
) -> Response:
    refresh_token = request.cookies.get(_REFRESH_COOKIE) or (body.refresh_token if body else None)
    if not refresh_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="refresh_token이 없습니다.")

    try:
        payload = security.verify_token(refresh_token, aud="refresh")
    except Exception as exc:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 refresh_token"
        ) from exc

    try:
        await store.rotate(payload.sub, payload.jti)
    except RefreshReuseDetectedError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    access_token, new_refresh_token = issue_token_pair(payload.sub, aud=API_AUD)
    new_payload = security.verify_token(new_refresh_token, aud="refresh")
    await store.register(payload.sub, new_payload.jti, REFRESH_TOKEN_TTL_SECONDS)

    response = Response(
        content=TokenResponse(
            access_token=access_token, expires_in=_ACCESS_TOKEN_EXPIRES_MIN * 60
        ).model_dump_json(),
        media_type="application/json",
    )
    _set_token_cookies(response, access_token, new_refresh_token)
    return response


@router.post("/logout")
async def logout(
    request: Request, store: RefreshTokenStore = Depends(get_refresh_store)
) -> Response:
    refresh_token = request.cookies.get(_REFRESH_COOKIE)
    if refresh_token:
        try:
            payload = security.verify_token(refresh_token, aud="refresh")
            await store.revoke(payload.sub, payload.jti)
        except Exception:
            logger.info("[/auth/logout] 이미 무효한 refresh_token — 쿠키만 정리합니다.")

    response = Response(content='{"ok": true}', media_type="application/json")
    _clear_token_cookies(response)
    return response


@router.get("/.well-known/jwks.json")
async def jwks() -> dict[str, list[dict]]:
    return {"keys": [security.get_public_jwk()]}
