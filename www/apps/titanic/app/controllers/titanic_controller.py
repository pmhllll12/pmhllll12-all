"""HTTP(또는 앱 경계)에서 호출하는 진입점 — secom의 UserController와 같은 층."""

from __future__ import annotations

import pandas as pd

from titanic.app.services.titanic_service import TitanicService


class TitanicController:
    """타이타닉 데이터·모델 조회 API용 컨트롤러."""

    def __init__(self) -> None:
        self._service = TitanicService()

    def get_data(self) -> pd.DataFrame:
        """표본 1행(기존 WalterReader 동작 유지)."""
        return self._service.get_sample_passenger_records()

    def get_count(self) -> int:
        """전체 탑승객 행 수."""
        return self._service.get_passenger_count()

    def get_model_name_and_accuracy(self) -> dict[str, object]:
        """모델 메타데이터(JSON 직렬화 가능)."""
        return self._service.get_model_metadata()

    def has_decision_tree_model(self) -> bool:
        """의사결정나무 기반 분류기 사용 여부."""
        return self._service.has_decision_tree_classifier()
