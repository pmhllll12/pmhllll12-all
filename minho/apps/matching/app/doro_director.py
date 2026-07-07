"""Doro 데이터 디렉터 (스텁 — `/doro/data` 용)."""

from __future__ import annotations

import pandas as pd


class DoroDirector:
    def get_data(self) -> pd.DataFrame:
        return pd.DataFrame()
