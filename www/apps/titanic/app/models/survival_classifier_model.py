"""생존 이진 분류용 ML 래퍼 — 기존 RoseModel(DecisionTree) 역할."""

from __future__ import annotations

from sklearn.tree import DecisionTreeClassifier


class SurvivalClassifierModel:
    """Survived(0/1) 예측을 위한 의사결정나무 분류기 자리."""

    def __init__(self) -> None:
        self._estimator = DecisionTreeClassifier()

    def is_decision_tree(self) -> bool:
        return isinstance(self._estimator, DecisionTreeClassifier)

    def describe_for_api(self) -> dict[str, object]:
        return {
            "model": type(self._estimator).__name__,
            "accuracy": None,
            "task": "binary_classification",
            "target": "Survived",
        }
