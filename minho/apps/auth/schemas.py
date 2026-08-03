from __future__ import annotations

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="access token 만료까지 남은 초")


class LoginRequest(BaseModel):
    provider: str = Field(..., description="google | naver | kakao")
    return_to: str | None = Field(None, description="로그인 완료 후 돌아갈 프런트엔드 origin")


class RefreshRequest(BaseModel):
    refresh_token: str | None = Field(
        None, description="쿠키가 없을 때(예: 네이티브 클라이언트) 바디로 전달"
    )


# --- 모바일(Flutter) --------------------------------------------------------
# 모바일은 쿠키를 쓰지 않는다. 토큰은 항상 JSON 본문으로 오간다.


class KakaoMobileLoginRequest(BaseModel):
    access_token: str | None = Field(None, description="카카오 SDK가 받은 access token")
    id_token: str | None = Field(None, description="카카오 OIDC를 켠 앱만 함께 보낸다")


class MobileRefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="직전에 발급받은 refresh token")


class MobileTokenResponse(BaseModel):
    access_token: str
    refresh_token: str = Field(..., description="회전된 새 토큰 — 반드시 덮어써야 한다")
    token_type: str = "bearer"
    expires_in: int = Field(..., description="access token 만료까지 남은 초")
