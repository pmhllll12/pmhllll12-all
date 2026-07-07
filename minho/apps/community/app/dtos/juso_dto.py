from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class JusoQuery:
    id: int
    name: str


@dataclass(frozen=True)
class JusoResult:
    id: int
    name: str
    role: str
    responsibilities: tuple[str, ...]
    greeting: str


@dataclass(frozen=True)
class JusoContactRecord:
    first_name: str = ""
    middle_name: str = ""
    last_name: str = ""
    nickname: str = ""
    organization_name: str = ""
    organization_title: str = ""
    email_1_value: str = ""
    phone_1_value: str = ""
    phone_2_value: str = ""
    address_1_city: str = ""
    address_1_country: str = ""
    birthday: str = ""
    labels: str = ""


@dataclass(frozen=True)
class JusoUploadResult:
    ok: bool
    count: int
    message: str


@dataclass(frozen=True)
class JusoContactSuggestionResult:
    nickname: str
    email: str
