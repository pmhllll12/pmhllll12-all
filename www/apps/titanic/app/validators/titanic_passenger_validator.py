"""탑승객 레코드 단순 검증 — 기존 CaledonValidation 확장 자리."""

from __future__ import annotations

from typing import Any

# 본 저장소 CSV 헤더 기준( Boat 컬럼 없음 — 다른 소스 확장 시 보완)
_EXPECTED_COLUMNS = frozenset(
    {
        "PassengerId",
        "Survived",
        "Pclass",
        "Name",
        "Sex",
        "Age",
        "SibSp",
        "Parch",
        "Ticket",
        "Fare",
        "Cabin",
        "Embarked",
    }
)


class TitanicPassengerValidator:
    """선택적 행 검증(업로드·배치 전처리 시 확장)."""

    @staticmethod
    def row_has_core_columns(row: dict[str, Any]) -> bool:
        return _EXPECTED_COLUMNS.issubset(row.keys())
