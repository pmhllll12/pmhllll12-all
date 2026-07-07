"""레포지토리에 포함된 CSV 파일 없이 동일 스키마 데모 데이터만 제공."""

from __future__ import annotations

import pandas as pd


def titanic_demo_dataframe() -> pd.DataFrame:
    """Kaggle Titanic 스타일 최소 컬럼·20행 (파일 I/O 없음)."""
    return pd.DataFrame(
        {
            "PassengerId": list(range(1, 21)),
            "Survived": [0, 1, 1, 0, 0, 1, 0, 1, 1, 0] * 2,
            "Pclass": [3, 1, 3, 2, 3, 1, 3, 2, 1, 3] * 2,
            "Sex": [
                "male",
                "female",
                "female",
                "male",
                "male",
                "female",
                "male",
                "female",
                "female",
                "male",
            ]
            * 2,
            "Age": [22.0, 38.0, 26.0, 35.0, 35.0, 54.0, 2.0, 27.0, 14.0, 4.0] * 2,
            "SibSp": [1, 0, 1, 0, 0, 0, 3, 0, 1, 0] * 2,
            "Parch": [0, 0, 0, 0, 0, 0, 1, 2, 0, 0] * 2,
            "Fare": [7.25, 71.28, 7.93, 53.1, 8.05, 51.86, 21.08, 11.13, 30.07, 16.7] * 2,
            "Embarked": ["S", "C", "S", "S", "S", "S", "S", "S", "S", "S"] * 2,
        }
    )
