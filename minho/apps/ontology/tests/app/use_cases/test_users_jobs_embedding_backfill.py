from __future__ import annotations

import asyncio

from ontology.app.use_cases.users_jobs_embedding_backfill import (
    backfill_rows,
    build_job_text,
    build_user_text,
)


class _FakeEmbedder:
    def __init__(self, dim: int = 768, fail_on: str | None = None):
        self.dim = dim
        self.fail_on = fail_on
        self.calls: list[str] = []

    async def embed(self, text: str) -> list[float]:
        self.calls.append(text)
        if self.fail_on is not None and self.fail_on in text:
            raise RuntimeError("embed 실패")
        return [0.1] * self.dim


def test_build_user_text_includes_name_and_age():
    assert build_user_text("김민준", 32) == "김민준 32세"


def test_build_user_text_without_age():
    assert build_user_text("김민준", None) == "김민준"


def test_build_job_text_joins_title_and_company():
    assert build_job_text("백엔드 개발자", "카카오") == "백엔드 개발자 카카오"


def test_backfill_fills_every_row():
    embedder = _FakeEmbedder()
    rows = [(1, "김민준 32세"), (2, "이서연 28세")]
    saved: dict[int, list[float]] = {}

    async def save(row_id, vector):
        saved[row_id] = vector

    result = asyncio.run(backfill_rows(rows, embedder, save))

    assert result.filled == 2
    assert result.failed == 0
    assert len(saved[1]) == 768
    assert embedder.calls == ["김민준 32세", "이서연 28세"]


def test_backfill_skips_row_whose_embed_fails_and_continues():
    embedder = _FakeEmbedder(fail_on="이서연")
    rows = [(1, "김민준 32세"), (2, "이서연 28세"), (3, "박도윤 41세")]
    saved: dict[int, list[float]] = {}

    async def save(row_id, vector):
        saved[row_id] = vector

    result = asyncio.run(backfill_rows(rows, embedder, save))

    assert result.filled == 2
    assert result.failed == 1
    assert set(saved) == {1, 3}


def test_backfill_rejects_wrong_dimension_vector():
    embedder = _FakeEmbedder(dim=512)
    rows = [(1, "김민준 32세")]
    saved: dict[int, list[float]] = {}

    async def save(row_id, vector):
        saved[row_id] = vector

    result = asyncio.run(backfill_rows(rows, embedder, save))

    assert result.filled == 0
    assert result.failed == 1
    assert saved == {}
