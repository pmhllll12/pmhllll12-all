from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SendEmailCommand:
    to_email: str
    topic: str


@dataclass(frozen=True)
class SendEmailResult:
    ok: bool
    message: str
