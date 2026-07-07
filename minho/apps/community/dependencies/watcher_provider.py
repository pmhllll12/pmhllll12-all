from __future__ import annotations

from fastapi import Depends

from community.adapter.outbound.repositories.watcher_repository import WatcherRepository
from community.app.ports.input.receiver_use_case import ReceiverUseCase
from community.app.ports.input.watcher_use_case import WatcherUseCase
from community.app.ports.output.content_filter_port import ContentFilterPort
from community.app.ports.output.watcher_port import WatcherPort
from community.app.use_cases.watcher_interactor import WatcherInteractor
from community.dependencies.providers import get_content_filter_port
from community.dependencies.receiver_provider import get_receiver_use_case


def get_watcher_repository() -> WatcherPort:
    return WatcherRepository()


def get_watcher_use_case(
    repository: WatcherPort = Depends(get_watcher_repository),
    content_filter: ContentFilterPort = Depends(get_content_filter_port),
    receiver_use_case: ReceiverUseCase = Depends(get_receiver_use_case),
) -> WatcherUseCase:
    return WatcherInteractor(
        repository=repository,
        content_filter=content_filter,
        receiver_use_case=receiver_use_case,
    )
