from __future__ import annotations

import logging
from datetime import datetime

from community.adapter.inbound.api.schemas.watcher_schemas import WatcherHostResponse, WatcherSchema
from community.app.dtos.watcher_dto import (
    WatcherHostQuery,
    WatcherJourneyLog,
    WatchEventCommand,
    WatchEventResult,
)
from community.app.dtos.receiver_dto import ReceiveEmailCommand
from community.app.ports.input.receiver_use_case import ReceiverUseCase
from community.app.ports.input.watcher_use_case import WatcherUseCase
from community.app.ports.output.content_filter_port import ContentFilterPort
from community.app.ports.output.watcher_port import WatcherPort
from community.domain.watcher_event import WatcherEvent
from community.domain.watcher_host import WatcherHost

logger = logging.getLogger(__name__)

_REPORT_INTENT_KEYWORDS = ("보고서", "리포트", "실적")


class WatcherInteractor(WatcherUseCase):
    """왓슨(Watson) — 인바운드 이벤트를 초진(Triage)해 홈즈(Holmes) 자체 처리 또는
    스타크래프트 온톨로지 버스를 경유한 페이커(Faker) 에스컬레이션으로 라우팅한다.

    star_craft·sherlock_homes 스포크가 아직 없어, 이 하네스는 라우팅 저니를
    community 앱 안에서 자기완결적으로 시뮬레이션한다.
    """

    def __init__(
        self,
        repository: WatcherPort,
        content_filter: ContentFilterPort,
        receiver_use_case: ReceiverUseCase,
    ) -> None:
        self.repository = repository
        self.content_filter = content_filter
        self.receiver_use_case = receiver_use_case

    async def introduce_myself(self, schema: WatcherSchema) -> WatcherHostResponse:
        query = WatcherHostQuery(id=schema.id, name=schema.name)
        host = WatcherHost.default()
        return WatcherHostResponse(
            id=query.id,
            name=host.name,
            role=host.role,
            features=list(host.features),
            greeting=host.greeting,
        )

    async def watch(self, command: WatchEventCommand) -> WatchEventResult:
        event = WatcherEvent(
            channel=command.channel,
            sender=command.sender,
            content=command.content,
            important_client=command.important_client,
        )
        steps = [f"Watson 인입: channel={event.channel} sender={event.sender}"]

        if not await self.filter_stop_word(event.content):
            steps.append("Llama-3.1-8B-Instruct 필터: 비정상 콘텐츠 감지 — 처리 중단")
            for step in steps:
                logger.info("[Watson] %s", step)
            log = WatcherJourneyLog(
                received_at=datetime.now().isoformat(),
                channel=event.channel,
                sender=event.sender,
                route="blocked",
                steps=steps,
            )
            await self.repository.save(log)
            return WatchEventResult(
                ok=False, route="blocked", message="비정상 콘텐츠로 판정되어 처리가 중단되었습니다."
            )
        steps.append("Llama-3.1-8B-Instruct 필터: 정상 콘텐츠 확인")

        await self.receiver_use_case.receive(
            ReceiveEmailCommand(
                subject=f"[{event.channel}] {event.sender}",
                from_=event.sender,
                to=None,
                body=event.content,
            )
        )
        steps.append("receiver 파이프라인 경유 pgvector 저장 완료")

        if event.important_client or self._has_report_intent(event.content):
            steps.append("Watson 분류: Case B (중요 거래처/보고서 요청 — 에스컬레이션)")
            steps.append("StarCraft 온톨로지 버스 경유")
            steps.append("Faker(EXAONE) 활성화(Wake-up) — 전사 ERP 데이터 취합 후 보고서 생성")
            route = "faker"
            message = "star_craft를 경유해 페이커로 에스컬레이션되었습니다."
        else:
            steps.append("Watson 분류: Case A (일반 업무)")
            steps.append("Holmes 자체 처리 — 컨텍스트 소화 및 종결")
            route = "holmes"
            message = "홈즈가 자체 처리했습니다."

        steps.append("처리 완료")
        for step in steps:
            logger.info("[Watson] %s", step)

        log = WatcherJourneyLog(
            received_at=datetime.now().isoformat(),
            channel=event.channel,
            sender=event.sender,
            route=route,
            steps=steps,
        )
        await self.repository.save(log)
        return WatchEventResult(ok=True, route=route, message=message)

    async def get_logs(self) -> list[WatcherJourneyLog]:
        return await self.repository.list_recent()

    async def filter_stop_word(self, content: str) -> bool:
        """비속어 필터 — Llama-3.1-8B-Instruct로 정상 콘텐츠만 통과시킨다."""
        return await self.content_filter.is_normal(content)

    @staticmethod
    def _has_report_intent(content: str) -> bool:
        return any(keyword in content for keyword in _REPORT_INTENT_KEYWORDS)
