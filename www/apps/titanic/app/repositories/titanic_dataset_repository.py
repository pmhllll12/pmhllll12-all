"""Titanic 데이터 접근 — 저장소에 CSV 파일을 두지 않고 데모 프레임만 사용."""

from __future__ import annotations

import pandas as pd

from titanic.app.demo_data import titanic_demo_dataframe


class TitanicDatasetRepository:
    """Kaggle식 Titanic 탑승객 스키마(메모리 데모)."""

    def get_preview_row_dataframe(self) -> pd.DataFrame:
        """첫 행만 JSON 응답용으로 반환."""
        df = titanic_demo_dataframe()
        row = df.iloc[[0]].astype(object).where(df.iloc[[0]].notna(), None)
        return row

    def count_passengers(self) -> int:
        return int(len(titanic_demo_dataframe()))

    def load_full_dataframe(self) -> pd.DataFrame:
        """학습·분석용 전체 프레임."""
        return titanic_demo_dataframe()
