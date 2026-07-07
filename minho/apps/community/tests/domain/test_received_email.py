from __future__ import annotations

from datetime import datetime

import pytest
from community.domain.received_email import ReceivedEmail


def test_valid_received_email():
    email = ReceivedEmail(
        subject="안녕하세요",
        from_="a@b.com",
        to="c@d.com",
        body="본문",
        received_at=datetime(2026, 7, 2, 12, 0, 0),
    )
    assert email.subject == "안녕하세요"
    assert email.from_ == "a@b.com"


def test_blank_subject_raises():
    with pytest.raises(ValueError, match="subject는 비어 있을 수 없습니다"):
        ReceivedEmail(subject="   ", from_=None, to=None, body=None, received_at=datetime.now())


def test_optional_fields_can_be_none():
    email = ReceivedEmail(
        subject="제목", from_=None, to=None, body=None, received_at=datetime.now()
    )
    assert email.from_ is None
    assert email.to is None
    assert email.body is None


def test_immutable():
    email = ReceivedEmail(
        subject="제목", from_=None, to=None, body=None, received_at=datetime.now()
    )
    with pytest.raises(Exception):
        email.subject = "다른 제목"  # type: ignore[misc]
