from __future__ import annotations

import asyncio

import pytest

from community.app.dtos.send_email_dto import SendEmailCommand
from community.app.ports.output.email_client_port import EmailClientPort
from community.app.use_cases.send_email_interactor import SendEmailInteractor


class _StubClientOk(EmailClientPort):
    async def deliver(self, to_email: str, topic: str) -> bool:
        return True


class _StubClientFail(EmailClientPort):
    async def deliver(self, to_email: str, topic: str) -> bool:
        return False


def test_send_success():
    async def _run():
        interactor = SendEmailInteractor(client=_StubClientOk())
        return await interactor.send(SendEmailCommand(to_email="a@b.com", topic="테스트 주제"))

    result = asyncio.run(_run())
    assert result.ok is True
    assert "a@b.com" in result.message


def test_send_failure():
    async def _run():
        interactor = SendEmailInteractor(client=_StubClientFail())
        return await interactor.send(SendEmailCommand(to_email="a@b.com", topic="테스트 주제"))

    result = asyncio.run(_run())
    assert result.ok is False
    assert "실패" in result.message


def test_invalid_email_raises():
    async def _run():
        interactor = SendEmailInteractor(client=_StubClientOk())
        return await interactor.send(SendEmailCommand(to_email="bademail", topic="주제"))

    with pytest.raises(ValueError, match="유효하지 않은 이메일"):
        asyncio.run(_run())
