from __future__ import annotations

import asyncio

from community.adapter.inbound.api.schemas.watcher_schemas import WatcherSchema
from community.app.dtos.receiver_dto import (
    ReceivedEmailLog,
    ReceiveEmailCommand,
    ReceiveEmailResult,
)
from community.app.dtos.watcher_dto import WatcherJourneyLog, WatchEventCommand
from community.app.ports.input.receiver_use_case import ReceiverUseCase
from community.app.ports.output.content_filter_port import ContentFilterPort
from community.app.ports.output.watcher_port import WatcherPort
from community.app.use_cases.watcher_interactor import WatcherInteractor


class _StubRepository(WatcherPort):
    def __init__(self) -> None:
        self.saved: list[WatcherJourneyLog] = []

    async def save(self, log: WatcherJourneyLog) -> None:
        self.saved.append(log)

    async def list_recent(self, limit: int = 100) -> list[WatcherJourneyLog]:
        return self.saved[:limit]


class _StubContentFilter(ContentFilterPort):
    def __init__(self, normal: bool = True) -> None:
        self.normal = normal
        self.calls: list[str] = []

    async def is_normal(self, content: str) -> bool:
        self.calls.append(content)
        return self.normal


class _StubReceiverUseCase(ReceiverUseCase):
    def __init__(self) -> None:
        self.received: list[ReceiveEmailCommand] = []

    async def receive(self, command: ReceiveEmailCommand) -> ReceiveEmailResult:
        self.received.append(command)
        return ReceiveEmailResult(ok=True, message="received")

    async def get_logs(self) -> list[ReceivedEmailLog]:
        return []


def _make_interactor(
    normal: bool = True,
) -> tuple[WatcherInteractor, _StubRepository, _StubContentFilter, _StubReceiverUseCase]:
    repository = _StubRepository()
    content_filter = _StubContentFilter(normal=normal)
    receiver_use_case = _StubReceiverUseCase()
    interactor = WatcherInteractor(
        repository=repository,
        content_filter=content_filter,
        receiver_use_case=receiver_use_case,
    )
    return interactor, repository, content_filter, receiver_use_case


def test_introduce_myself_returns_watson_profile():
    async def _run():
        interactor, *_ = _make_interactor()
        return await interactor.introduce_myself(WatcherSchema(id=6, name="왓슨"))

    result = asyncio.run(_run())
    assert result.name == "왓슨 (Watson)"
    assert "Holmes" in " ".join(result.features) or "홈즈" in " ".join(result.features)


def test_scenario1_normal_inquiry_routes_to_holmes():
    """Scenario 1: 일반 거래처의 단순 인사/문의 메일 인입 → 홈즈 자체 처리."""

    async def _run():
        interactor, repository, _, receiver_use_case = _make_interactor()
        result = await interactor.watch(
            WatchEventCommand(
                channel="email",
                sender="normal@client.com",
                content="안녕하세요, 문의드립니다.",
                important_client=False,
            )
        )
        return repository, receiver_use_case, result

    repository, receiver_use_case, result = asyncio.run(_run())
    assert result.ok is True
    assert result.route == "holmes"
    assert len(repository.saved) == 1
    assert repository.saved[0].route == "holmes"
    assert len(receiver_use_case.received) == 1


def test_scenario2_vip_report_request_escalates_to_faker():
    """Scenario 2: VIP 거래처의 분기 실적 자동 보고서 발행 요망 → 페이커 에스컬레이션."""

    async def _run():
        interactor, repository, *_ = _make_interactor()
        result = await interactor.watch(
            WatchEventCommand(
                channel="email",
                sender="vip@client.com",
                content="분기 실적 자동 보고서 발행을 요청합니다.",
                important_client=True,
            )
        )
        return repository, result

    repository, result = asyncio.run(_run())
    assert result.ok is True
    assert result.route == "faker"
    assert "StarCraft" in " ".join(repository.saved[0].steps)


def test_report_intent_without_important_flag_still_escalates():
    async def _run():
        interactor, *_ = _make_interactor()
        return await interactor.watch(
            WatchEventCommand(
                channel="discord",
                sender="unknown",
                content="이번 분기 실적 보고서 부탁드립니다.",
                important_client=False,
            )
        )

    result = asyncio.run(_run())
    assert result.route == "faker"


def test_get_logs_returns_saved_journeys():
    async def _run():
        interactor, *_ = _make_interactor()
        await interactor.watch(
            WatchEventCommand(
                channel="telegram", sender="a", content="안녕", important_client=False
            )
        )
        return await interactor.get_logs()

    logs = asyncio.run(_run())
    assert len(logs) == 1
    assert logs[0].channel == "telegram"


def test_blocked_content_skips_receiver_pipeline():
    async def _run():
        interactor, repository, content_filter, receiver_use_case = _make_interactor(normal=False)
        result = await interactor.watch(
            WatchEventCommand(
                channel="discord",
                sender="spammer",
                content="비속어가 섞인 내용",
                important_client=False,
            )
        )
        return repository, content_filter, receiver_use_case, result

    repository, content_filter, receiver_use_case, result = asyncio.run(_run())
    assert result.ok is False
    assert result.route == "blocked"
    assert len(content_filter.calls) == 1
    assert len(receiver_use_case.received) == 0
    assert repository.saved[0].route == "blocked"


def test_normal_content_forwards_to_receiver_pipeline():
    async def _run():
        interactor, _, _, receiver_use_case = _make_interactor(normal=True)
        await interactor.watch(
            WatchEventCommand(
                channel="email",
                sender="normal@client.com",
                content="정상적인 문의입니다.",
                important_client=False,
            )
        )
        return receiver_use_case

    receiver_use_case = asyncio.run(_run())
    assert len(receiver_use_case.received) == 1
    assert receiver_use_case.received[0].body == "정상적인 문의입니다."
