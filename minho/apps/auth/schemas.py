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
