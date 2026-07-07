"""비즈니스 유스케이스 — 저장소·모델을 조합 (secom UserService와 같은 층)."""

from __future__ import annotations

import pandas as pd

from titanic.app.models.survival_classifier_model import SurvivalClassifierModel
from titanic.app.repositories.titanic_dataset_repository import TitanicDatasetRepository


class TitanicService:
    """생존 이진 분류 맥락에서 데이터 조회·모델 정보 제공."""

    def __init__(self) -> None:
        self._repository = TitanicDatasetRepository()
        self._model = SurvivalClassifierModel()

    def get_sample_passenger_records(self) -> pd.DataFrame:
        return self._repository.get_preview_row_dataframe()

    def get_passenger_count(self) -> int:
        return self._repository.count_passengers()

    def get_model_metadata(self) -> dict[str, object]:
        return self._model.describe_for_api()

    def has_decision_tree_classifier(self) -> bool:
        return self._model.is_decision_tree()
