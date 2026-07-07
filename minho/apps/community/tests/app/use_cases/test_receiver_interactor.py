from __future__ import annotations

import asyncio
from datetime import datetime

import pytest

from community.app.dtos.receiver_dto import ReceivedEmailLog, ReceiveEmailCommand
from community.app.ports.output.content_filter_port import ContentFilterPort
from community.app.ports.output.embedding_port import EmbeddingPort
from community.app.ports.output.receiver_port import ReceiverPort
from community.app.use_cases.receiver_interactor import ReceiverInteractor


class _StubEmbedder(EmbeddingPort):
    def __init__(self) -> None:
        self.calls = 0

    async def embed(self, text: str) -> list[float]:
        self.calls += 1
        return [0.1, 0.2, 0.3]


class _StubContentFilter(ContentFilterPort):
    def __init__(self, normal: bool = True) -> None:
        self.normal = normal
        self.calls = 0

    async def is_normal(self, content: str) -> bool:
        self.calls += 1
        return self.normal


class _StubRepository(ReceiverPort):
    def __init__(self) -> None:
        self.saved: list[dict] = []

    async def exists_by_message_id(self, message_id: str) -> bool:
        return any(row["message_id"] == message_id for row in self.saved)

    async def save(
        self,
        subject: str,
        from_: str | None,
        to: str | None,
        body: str | None,
        received_at: datetime,
        embedding: list[float],
        message_id: str | None = None,
    ) -> None:
        self.saved.append(
            {
                "subject": subject,
                "from_": from_,
                "to": to,
                "body": body,
                "received_at": received_at,
                "embedding": embedding,
                "message_id": message_id,
            }
        )

    async def list_recent(self, limit: int = 100) -> list[ReceivedEmailLog]:
        return [
            ReceivedEmailLog(
                received_at=row["received_at"].isoformat(),
                subject=row["subject"],
                from_=row["from_"],
                to=row["to"],
                body=row["body"],
                message_id=row["message_id"],
            )
            for row in self.saved
        ]


def _make_interactor(
    normal: bool = True,
) -> tuple[ReceiverInteractor, _StubRepository, _StubEmbedder, _StubContentFilter]:
    repository = _StubRepository()
    embedder = _StubEmbedder()
    content_filter = _StubContentFilter(normal=normal)
    interactor = ReceiverInteractor(
        repository=repository, embedder=embedder, content_filter=content_filter
    )
    return interactor, repository, embedder, content_filter


def test_receive_saves_with_embedding():
    async def _run():
        interactor, repository, *_ = _make_interactor()
        result = await interactor.receive(
            ReceiveEmailCommand(subject="제목", from_="a@b.com", to="c@d.com", body="본문")
        )
        return repository, result

    repository, result = asyncio.run(_run())
    assert result.ok is True
    assert len(repository.saved) == 1
    assert repository.saved[0]["subject"] == "제목"
    assert repository.saved[0]["embedding"] == [0.1, 0.2, 0.3]


def test_receive_blank_subject_raises():
    async def _run():
        interactor, *_ = _make_interactor()
        return await interactor.receive(
            ReceiveEmailCommand(subject="   ", from_=None, to=None, body=None)
        )

    with pytest.raises(ValueError, match="subject는 비어 있을 수 없습니다"):
        asyncio.run(_run())


def test_get_logs_returns_saved_entries():
    async def _run():
        interactor, *_ = _make_interactor()
        await interactor.receive(
            ReceiveEmailCommand(subject="제목", from_="a@b.com", to=None, body=None)
        )
        return await interactor.get_logs()

    logs = asyncio.run(_run())
    assert len(logs) == 1
    assert logs[0].subject == "제목"


def test_duplicate_message_id_is_skipped_without_embedding():
    async def _run():
        interactor, repository, embedder, _ = _make_interactor()
        first = await interactor.receive(
            ReceiveEmailCommand(
                subject="제목", from_="a@b.com", to=None, body=None, message_id="msg-1"
            )
        )
        second = await interactor.receive(
            ReceiveEmailCommand(
                subject="제목", from_="a@b.com", to=None, body=None, message_id="msg-1"
            )
        )
        return repository, embedder, first, second

    repository, embedder, first, second = asyncio.run(_run())
    assert first.ok is True
    assert second.ok is True
    assert len(repository.saved) == 1
    assert embedder.calls == 1


def test_different_message_id_is_saved_separately():
    async def _run():
        interactor, repository, *_ = _make_interactor()
        await interactor.receive(
            ReceiveEmailCommand(
                subject="제목1", from_="a@b.com", to=None, body=None, message_id="msg-1"
            )
        )
        await interactor.receive(
            ReceiveEmailCommand(
                subject="제목2", from_="a@b.com", to=None, body=None, message_id="msg-2"
            )
        )
        return repository

    repository = asyncio.run(_run())
    assert len(repository.saved) == 2


def test_blocked_content_is_not_saved_or_embedded():
    async def _run():
        interactor, repository, embedder, content_filter = _make_interactor(normal=False)
        result = await interactor.receive(
            ReceiveEmailCommand(
                subject="비속어 제목", from_="spam@bad.com", to=None, body="욕설 내용"
            )
        )
        return repository, embedder, content_filter, result

    repository, embedder, content_filter, result = asyncio.run(_run())
    assert result.ok is False
    assert len(repository.saved) == 0
    assert embedder.calls == 0
    assert content_filter.calls == 1
