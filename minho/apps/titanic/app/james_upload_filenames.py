"""James 업로드 — 파일명 제한 없음(컬럼 검증은 james_command)."""

from __future__ import annotations


def is_allowed_titanic_csv(filename: str) -> bool:
    """`.csv` 이면 허용 (`Titanic-Dataset.csv` 등 모든 이름 가능)."""
    return filename.strip().lower().endswith(".csv")
