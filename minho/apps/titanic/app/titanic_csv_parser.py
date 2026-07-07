"""Titanic Kaggle CSV 파싱 — Sex → gender 변환."""

from __future__ import annotations

import io
from typing import Any

import numpy as np
import pandas as pd

EXPECTED_COLUMNS: tuple[str, ...] = (
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
)

PREVIEW_LIMIT = 5

API_COLUMNS: tuple[str, ...] = tuple(
    "gender" if col == "Sex" else col for col in EXPECTED_COLUMNS
)


def parse_titanic_csv(content: bytes, filename: str) -> dict[str, Any]:
    if not content.strip():
        raise ValueError("파일이 비어 있습니다.")

    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"CSV를 읽을 수 없습니다: {exc}") from exc

    if df.empty:
        raise ValueError("데이터 행이 없습니다.")

    df.columns = [str(c).strip() for c in df.columns]
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"필수 컬럼이 없습니다: {', '.join(missing)}")

    df = df.loc[:, list(EXPECTED_COLUMNS)].copy()
    df = df.rename(columns={"Sex": "gender"})

    records = df.replace({np.nan: None}).to_dict(orient="records")

    return {
        "ok": True,
        "message": "CSV를 수신했습니다. Sex 열을 gender 로 변환했습니다.",
        "filename": filename,
        "row_count": int(len(df)),
        "columns": list(df.columns),
        "preview": records[:PREVIEW_LIMIT],
        "rows": records,
    }
