"""도로 사고 통계 예시 — 프로젝트 내 CSV 파일을 읽지 않습니다."""

from __future__ import annotations

import pandas as pd


def _demo_road_stats_row() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "연도": 2024,
                "발생건수": 105000,
                "사망자수": 2650,
                "중상자수": 8200,
                "경상자수": 71500,
            }
        ]
    )


class DoroReader:
    def get_data(self) -> pd.DataFrame:
        df = _demo_road_stats_row()
        return df.astype(object).where(df.notna(), None)
