"""역할·권한 정의. secom User 연동 없이 발급하므로(2026-07-22 결정), 모든 OAuth
로그인 사용자는 기본 Role.USER를 받는다 — 별도 권한 승격 경로가 생기기 전까지는
이 값이 유일한 role이다."""

from __future__ import annotations

from enum import Enum


class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"


class Permission(str, Enum):
    READ_OWN_PROFILE = "read:own_profile"
    MANAGE_USERS = "manage:users"


ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.USER: frozenset({Permission.READ_OWN_PROFILE}),
    Role.ADMIN: frozenset({Permission.READ_OWN_PROFILE, Permission.MANAGE_USERS}),
}

DEFAULT_ROLES: list[str] = [Role.USER.value]
