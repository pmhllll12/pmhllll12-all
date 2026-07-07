from __future__ import annotations

from fastapi import APIRouter, Depends

from community.adapter.inbound.api.schemas.watcher_schemas import (
    WatcherHostResponse,
    WatcherIncomingRequest,
    WatcherIncomingResponse,
    WatcherJourneyLogEntry,
    WatcherSchema,
)
from community.app.dtos.watcher_dto import WatchEventCommand
from community.app.ports.input.watcher_use_case import WatcherUseCase
from community.dependencies.watcher_provider import get_watcher_use_case

watcher_router = APIRouter(prefix="/watcher", tags=["community-watcher"])


@watcher_router.get("/myself", response_model=WatcherHostResponse)
async def introduce_myself(
    use_case: WatcherUseCase = Depends(get_watcher_use_case),
) -> WatcherHostResponse:
    return await use_case.introduce_myself(WatcherSchema(id=6, name="왓슨 (Watson)"))


@watcher_router.post("/incoming", response_model=WatcherIncomingResponse)
async def receive_watched_event(
    body: WatcherIncomingRequest,
    use_case: WatcherUseCase = Depends(get_watcher_use_case),
) -> WatcherIncomingResponse:
    """왓슨(Watson)이 인바운드 이벤트를 초진해 홈즈 또는 페이커(경유: 스타크래프트)로
    라우팅합니다."""
    result = await use_case.watch(
        WatchEventCommand(
            channel=body.channel,
            sender=body.sender,
            content=body.content,
            important_client=body.important_client,
        )
    )
    return WatcherIncomingResponse(ok=result.ok, route=result.route, message=result.message)


@watcher_router.get("/logs", response_model=list[WatcherJourneyLogEntry])
async def get_watcher_logs(
    use_case: WatcherUseCase = Depends(get_watcher_use_case),
) -> list[WatcherJourneyLogEntry]:
    """왓슨 라우팅 저니(narrative log)를 최신순으로 반환합니다 (최대 100건)."""
    logs = await use_case.get_logs()
    return [
        WatcherJourneyLogEntry(
            received_at=log.received_at,
            channel=log.channel,
            sender=log.sender,
            route=log.route,
            steps=log.steps,
        )
        for log in logs
    ]
