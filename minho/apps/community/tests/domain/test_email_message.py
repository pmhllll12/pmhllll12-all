from __future__ import annotations

import pytest

from community.domain.email_message import EmailMessage


def test_valid_email_message():
    msg = EmailMessage(to_email="user@example.com", topic="안녕하세요")
    assert msg.to_email == "user@example.com"
    assert msg.topic == "안녕하세요"


def test_email_without_at_sign_raises():
    with pytest.raises(ValueError, match="유효하지 않은 이메일"):
        EmailMessage(to_email="notanemail", topic="주제")


def test_empty_email_raises():
    with pytest.raises(ValueError, match="유효하지 않은 이메일"):
        EmailMessage(to_email="", topic="주제")


def test_blank_topic_raises():
    with pytest.raises(ValueError, match="topic은 비어 있을 수 없습니다"):
        EmailMessage(to_email="user@example.com", topic="   ")


def test_immutable():
    msg = EmailMessage(to_email="user@example.com", topic="주제")
    with pytest.raises(Exception):
        msg.to_email = "other@example.com"  # type: ignore[misc]
