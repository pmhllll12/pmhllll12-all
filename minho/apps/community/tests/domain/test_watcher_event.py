from __future__ import annotations

import pytest
from community.domain.watcher_event import WatcherEvent


def test_valid_watcher_event():
    event = WatcherEvent(
        channel="telegram", sender="user1", content="안녕하세요", important_client=False
    )
    assert event.channel == "telegram"
    assert event.important_client is False


def test_blank_channel_raises():
    with pytest.raises(ValueError, match="channel은 비어 있을 수 없습니다"):
        WatcherEvent(channel="   ", sender="user1", content="내용", important_client=False)


def test_blank_content_raises():
    with pytest.raises(ValueError, match="content는 비어 있을 수 없습니다"):
        WatcherEvent(channel="discord", sender="user1", content="   ", important_client=False)


def test_immutable():
    event = WatcherEvent(channel="discord", sender="user1", content="내용", important_client=True)
    with pytest.raises(Exception):
        event.channel = "telegram"  # type: ignore[misc]
