"""Walter 승객 명단 CSV → Neon 출력 포트 (`crew_walter_roaster` 캐릭터 포트와 별개)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@dataclass(slots=True, frozen=True)
class WalterPersistPayload:
    filename: str
    columns: list[str]
    rows: list[dict[str, Any]]


@runtime_checkable
class WalterPort(Protocol):
    """Neon `titanic_walter_passengers` 등에 대한 비동기 저장·조회."""

    async def persist_payload(self, payload: WalterPersistPayload) -> int:
        """정규화된 행 묶음을 저장합니다."""
        ...

    async def load_all_rows(self) -> list[dict[str, Any]]:
        """저장된 승객 행을 API 형식으로 반환합니다."""
        ...

    async def save_upload(
        self,
        *,
        filename: str,
        columns: list[str],
        rows: list[dict[str, Any]],
    ) -> int:
        """업로드 스냅샷을 저장합니다."""
        ...

    async def fetch_all(self) -> list[dict[str, Any]]:
        """전체 승객 행을 조회합니다."""
        ...

    @staticmethod
    def api_columns() -> list[str]:
        """API 컬럼 순서."""
        ...


async def submit_persist_upload(repository: WalterPort, payload: WalterPersistPayload) -> int:
    return await repository.persist_payload(payload)


async def submit_fetch_all_passengers(repository: WalterPort) -> list[dict[str, Any]]:
    return await repository.load_all_rows()


__all__ = [
    "WalterPersistPayload",
    "WalterPort",
    "submit_fetch_all_passengers",
    "submit_persist_upload",
]
