from __future__ import annotations

import asyncio

from moneyball.app.dtos.player_embedding_dto import BackfillCommand, PlayerProfile
from moneyball.app.ports.output.embedding_port import EmbeddingPort
from moneyball.app.ports.output.player_embedding_port import PlayerEmbeddingPort
from moneyball.app.use_cases.player_embedding_backfill_interactor import (
    PlayerEmbeddingBackfillInteractor,
)

_FAILING_NAME = "임베딩실패"


class _StubEmbeddingPort(EmbeddingPort):
    """이름에 `_FAILING_NAME` 이 들어간 선수만 실패하는 스텁."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    async def embed(self, text: str) -> list[float]:
        self.calls.append(text)
        if _FAILING_NAME in text:
            raise RuntimeError("gemini 429")
        return [float(len(text)), 0.5, -0.5]


class _StubPlayerEmbeddingPort(PlayerEmbeddingPort):
    def __init__(
        self, profiles: list[PlayerProfile], already_embedded: set[str] | None = None
    ) -> None:
        self._profiles = sorted(profiles, key=lambda p: p.player_id)
        self._already_embedded = set(already_embedded or set())
        self.saved: dict[str, list[float]] = {}
        self.commits = 0

    async def list_targets(
        self, limit: int, overwrite: bool, after_player_id: str | None = None
    ) -> list[PlayerProfile]:
        rows = self._profiles
        if after_player_id is not None:
            rows = [p for p in rows if p.player_id > after_player_id]
        if not overwrite:
            filled = self._already_embedded | set(self.saved)
            rows = [p for p in rows if p.player_id not in filled]
        return rows[:limit]

    async def save_embedding(self, player_id: str, embedding: list[float]) -> None:
        self.saved[player_id] = embedding

    async def commit(self) -> None:
        self.commits += 1


def _profile(player_id: str, player_name: str | None = "선수") -> PlayerProfile:
    return PlayerProfile(player_id=player_id, player_name=player_name, position="FW")


def _run(coro):
    return asyncio.run(coro)


def test_backfills_every_player_missing_an_embedding():
    players = _StubPlayerEmbeddingPort([_profile("p1"), _profile("p2"), _profile("p3")])
    embeddings = _StubEmbeddingPort()
    interactor = PlayerEmbeddingBackfillInteractor(players=players, embeddings=embeddings)

    result = _run(interactor.backfill(BackfillCommand()))

    assert result.targeted == 3
    assert result.updated == 3
    assert result.skipped == 0
    assert result.failed == 0
    assert set(players.saved) == {"p1", "p2", "p3"}
    assert players.commits >= 1


def test_player_without_any_name_is_skipped_and_never_embedded():
    players = _StubPlayerEmbeddingPort([_profile("p1"), _profile("p2", player_name=None)])
    embeddings = _StubEmbeddingPort()
    interactor = PlayerEmbeddingBackfillInteractor(players=players, embeddings=embeddings)

    result = _run(interactor.backfill(BackfillCommand()))

    assert result.updated == 1
    assert result.skipped == 1
    assert set(players.saved) == {"p1"}
    assert len(embeddings.calls) == 1


def test_embedding_failure_is_counted_and_does_not_stop_the_run():
    players = _StubPlayerEmbeddingPort(
        [_profile("p1"), _profile("p2", player_name=_FAILING_NAME), _profile("p3")]
    )
    embeddings = _StubEmbeddingPort()
    interactor = PlayerEmbeddingBackfillInteractor(players=players, embeddings=embeddings)

    result = _run(interactor.backfill(BackfillCommand()))

    assert result.failed == 1
    assert result.updated == 2
    assert set(players.saved) == {"p1", "p3"}


def test_limit_caps_the_number_of_players_processed():
    players = _StubPlayerEmbeddingPort([_profile(f"p{i}") for i in range(1, 6)])
    embeddings = _StubEmbeddingPort()
    interactor = PlayerEmbeddingBackfillInteractor(players=players, embeddings=embeddings)

    result = _run(interactor.backfill(BackfillCommand(limit=2, batch_size=20)))

    assert result.targeted == 2
    assert result.updated == 2
    assert len(players.saved) == 2


def test_dry_run_neither_embeds_nor_saves_but_returns_previews():
    players = _StubPlayerEmbeddingPort([_profile("p1"), _profile("p2")])
    embeddings = _StubEmbeddingPort()
    interactor = PlayerEmbeddingBackfillInteractor(players=players, embeddings=embeddings)

    result = _run(interactor.backfill(BackfillCommand(dry_run=True)))

    assert result.targeted == 2
    assert result.updated == 0
    assert embeddings.calls == []
    assert players.saved == {}
    assert players.commits == 0
    assert result.previews == ["이름 선수, 포지션 FW", "이름 선수, 포지션 FW"]


def test_batching_advances_past_skipped_players_instead_of_refetching_them():
    # 건너뛴 행은 embedding 이 계속 NULL 이라, 커서 없이 재조회하면 무한 루프가 된다.
    players = _StubPlayerEmbeddingPort(
        [_profile("p1"), _profile("p2", player_name=None), _profile("p3")]
    )
    embeddings = _StubEmbeddingPort()
    interactor = PlayerEmbeddingBackfillInteractor(players=players, embeddings=embeddings)

    result = _run(interactor.backfill(BackfillCommand(batch_size=1)))

    assert result.targeted == 3
    assert result.updated == 2
    assert result.skipped == 1
    assert players.commits == 2  # 임베딩을 저장한 배치에서만 커밋


def test_overwrite_reembeds_players_that_already_have_an_embedding():
    players = _StubPlayerEmbeddingPort(
        [_profile("p1"), _profile("p2")], already_embedded={"p1", "p2"}
    )
    embeddings = _StubEmbeddingPort()
    interactor = PlayerEmbeddingBackfillInteractor(players=players, embeddings=embeddings)

    without_overwrite = _run(interactor.backfill(BackfillCommand()))
    assert without_overwrite.targeted == 0

    with_overwrite = _run(interactor.backfill(BackfillCommand(overwrite=True)))
    assert with_overwrite.updated == 2
    assert set(players.saved) == {"p1", "p2"}
