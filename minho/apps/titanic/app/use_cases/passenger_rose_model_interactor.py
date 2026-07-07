from __future__ import annotations

import asyncio
from typing import Any

import numpy as np
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from titanic.adapter.inbound.api.schemas.passenger_rose_model_schemas import RoseModelSchema
from titanic.app.dtos.passenger_rose_model_dto import RoseModelQuery, RoseModelResponse
from titanic.app.ports.input.passenger_rose_model_use_case import (
    RoseModelStrategy,
    RoseModelUseCase,
)
from titanic.app.ports.output.passenger_rose_model_port import RoseModelPort
from xgboost import XGBClassifier


class LogisticRegressionStrategy(RoseModelStrategy):
    """5. Logistic Regression — 해석이 쉬운 베이스라인 분류 모델."""

    name = "logistic_regression"

    def __init__(self) -> None:
        self._model = LogisticRegression(max_iter=1000)

    def fit(self, features: Any, target: Any) -> None:
        self._model.fit(features, target)

    def predict(self, features: Any) -> Any:
        return self._model.predict(features)


class RandomForestStrategy(RoseModelStrategy):
    """2. Random Forest — 튜닝 없이도 안정적인 배깅 기반 모델."""

    name = "random_forest"

    def __init__(self) -> None:
        self._model = RandomForestClassifier()

    def fit(self, features: Any, target: Any) -> None:
        self._model.fit(features, target)

    def predict(self, features: Any) -> Any:
        return self._model.predict(features)


class DecisionTreeStrategy(RoseModelStrategy):
    """6. Decision Tree — 규칙 기반의 직관적인 트리 모델."""

    name = "decision_tree"

    def __init__(self) -> None:
        self._model = DecisionTreeClassifier()

    def fit(self, features: Any, target: Any) -> None:
        self._model.fit(features, target)

    def predict(self, features: Any) -> Any:
        return self._model.predict(features)


class SupportVectorMachineStrategy(RoseModelStrategy):
    """7. SVM — 마진을 최대화하는 결정 경계 탐색."""

    name = "svm"

    def __init__(self) -> None:
        self._model = SVC()

    def fit(self, features: Any, target: Any) -> None:
        self._model.fit(features, target)

    def predict(self, features: Any) -> Any:
        return self._model.predict(features)


class KNearestNeighborsStrategy(RoseModelStrategy):
    """8. KNN — 가까운 K개 이웃 기준 분류."""

    name = "knn"

    def __init__(self) -> None:
        self._model = KNeighborsClassifier()

    def fit(self, features: Any, target: Any) -> None:
        self._model.fit(features, target)

    def predict(self, features: Any) -> Any:
        return self._model.predict(features)


class NaiveBayesStrategy(RoseModelStrategy):
    """9. Naive Bayes — 베이즈 정리 기반 조건부 확률 분류."""

    name = "naive_bayes"

    def __init__(self) -> None:
        self._model = GaussianNB()

    def fit(self, features: Any, target: Any) -> None:
        self._model.fit(features, target)

    def predict(self, features: Any) -> Any:
        return self._model.predict(features)


class XgBoostStrategy(RoseModelStrategy):
    """1. XGBoost — 강한 규제로 과적합을 방지하는 그래디언트 부스팅."""

    name = "xgboost"

    def __init__(self) -> None:
        self._model = XGBClassifier(eval_metric="logloss")

    def fit(self, features: Any, target: Any) -> None:
        self._model.fit(features, target)

    def predict(self, features: Any) -> Any:
        return self._model.predict(features)


class LightGbmStrategy(RoseModelStrategy):
    """3. LightGBM — 리프 중심 분할로 빠르고 우수한 성능."""

    name = "lightgbm"

    def __init__(self) -> None:
        self._model = LGBMClassifier()

    def fit(self, features: Any, target: Any) -> None:
        self._model.fit(features, target)

    def predict(self, features: Any) -> Any:
        return self._model.predict(features)


class CatBoostStrategy(RoseModelStrategy):
    """4. CatBoost — 범주형 피처를 별도 인코딩 없이 최적화."""

    name = "catboost"

    def __init__(self) -> None:
        self._model = CatBoostClassifier(verbose=False)

    def fit(self, features: Any, target: Any) -> None:
        self._model.fit(features, target)

    def predict(self, features: Any) -> Any:
        return self._model.predict(features)


class KMeansPcaStrategy(RoseModelStrategy):
    """10. K-Means & PCA — 군집·차원축소로 보조 피처를 만들고 그 위에서 분류한다."""

    name = "kmeans_pca"

    def __init__(self, n_components: int = 2, n_clusters: int = 2) -> None:
        self._pca = PCA(n_components=n_components)
        self._kmeans = KMeans(n_clusters=n_clusters, n_init=10)
        self._classifier = LogisticRegression(max_iter=1000)

    def _augment(self, features: Any) -> Any:
        reduced = self._pca.transform(features)
        clusters = self._kmeans.predict(features).reshape(-1, 1)
        return np.hstack([reduced, clusters])

    def fit(self, features: Any, target: Any) -> None:
        self._pca.fit(features)
        self._kmeans.fit(features)
        self._classifier.fit(self._augment(features), target)

    def predict(self, features: Any) -> Any:
        return self._classifier.predict(self._augment(features))


STRATEGY_REGISTRY: dict[str, type[RoseModelStrategy]] = {
    strategy_cls.name: strategy_cls
    for strategy_cls in (
        XgBoostStrategy,
        RandomForestStrategy,
        LightGbmStrategy,
        CatBoostStrategy,
        LogisticRegressionStrategy,
        DecisionTreeStrategy,
        SupportVectorMachineStrategy,
        KNearestNeighborsStrategy,
        NaiveBayesStrategy,
        KMeansPcaStrategy,
    )
}


def create_strategy(name: str) -> RoseModelStrategy:
    try:
        return STRATEGY_REGISTRY[name]()
    except KeyError as exc:
        raise ValueError(f"알 수 없는 RoseModel 전략: {name}") from exc


class RoseModelInteractor(RoseModelUseCase):
    def __init__(
        self,
        repository: RoseModelPort,
        strategy: RoseModelStrategy | None = None,
    ) -> None:
        self.repository = repository
        self.strategy: RoseModelStrategy = strategy or LogisticRegressionStrategy()

    def set_strategy(self, strategy: RoseModelStrategy) -> None:
        """베이스라인(Logistic Regression)에서 다른 알고리즘으로 교체할 때 사용."""
        self.strategy = strategy

    async def train(self, features: Any, target: Any) -> None:
        await asyncio.to_thread(self.strategy.fit, features, target)

    async def predict(self, features: Any) -> Any:
        return await asyncio.to_thread(self.strategy.predict, features)

    async def introduce_myself(self, schema: RoseModelSchema) -> RoseModelResponse:
        query = RoseModelQuery(id=schema.id, name=schema.name)
        return await self.repository.introduce_myself(query)
