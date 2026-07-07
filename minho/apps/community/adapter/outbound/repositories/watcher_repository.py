from __future__ import annotations

from collections import deque

from community.app.dtos.watcher_dto import WatcherJourneyLog
from community.app.ports.output.watcher_port import WatcherPort

_journeys: deque[WatcherJourneyLog] = deque(maxlen=100)


class WatcherRepository(WatcherPort):
    """왓슨 라우팅 저니를 메모리에 보관한다 (테스트 하네스 — 서버 재시작 시 초기화)."""

    async def save(self, log: WatcherJourneyLog) -> None:
        _journeys.appendleft(log)

    async def list_recent(self, limit: int = 100) -> list[WatcherJourneyLog]:
        return list(_journeys)[:limit]
