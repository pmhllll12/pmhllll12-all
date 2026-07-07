from __future__ import annotations

import pandas as pd
from titanic.adapter.inbound.api.schemas.crew_lowe_boat_schema import LoweBoatSchema
from titanic.app.dtos.crew_lowe_boat_dto import LoweBoatQuery, LoweBoatResponse
from titanic.app.ports.input.crew_lowe_boat_use_case import LoweBoatUseCase
from titanic.app.ports.output.crew_lowe_boat_port import LoweBoatPort


class LoweBoatInteractor(LoweBoatUseCase):
    def __init__(self, repository: LoweBoatPort) -> None:
        self.repository = repository

    def feature_engineering(self, train_set):
        train = train_set.copy()

        # DB에서 모든 컬럼이 문자열로 올 수 있어 수치형 컬럼을 float으로 변환
        for col in ("Pclass", "Age"):
            train[col] = pd.to_numeric(train[col], errors="coerce")

        # 1. Label 분리
        y_label = train["Survived"].fillna(0).astype(int).tolist()
        train = train.drop("Survived", axis=1)

        # 2. 성별 Nominal 변환 (female=1, male=0)
        train["gender"] = train["gender"].map({"male": 0, "female": 1})

        # 3. 승선항 Nominal 변환
        train["Embarked"] = train["Embarked"].fillna("S").map({"S": 1, "C": 2, "Q": 3})

        # 4. 요금 Ordinal 변환 (train 기준 4분위 구간 정의)
        # DB에서 오는 Fare는 문자열로 들어올 수 있어 수치형으로 변환 후 분할
        train["Fare"] = pd.to_numeric(train["Fare"], errors="coerce")
        train["FareBand"] = (
            pd.qcut(train["Fare"], 4, labels=[1, 2, 3, 4], duplicates="drop")
            .fillna(1).astype(int)
        )

        # 5. 식별자성·중복 컬럼 제거 (Age는 생존 예측 질의에 필요해 피처로 유지)
        drop_cols = ["Name", "Fare", "Ticket", "Cabin", "PassengerId", "SibSp", "Parch"]
        train = train.drop(columns=[c for c in drop_cols if c in train.columns])

        # 6. 결측치 임퓨테이션 (Pclass는 booking 미매칭 시 NaN, gender도 비어 있으면 매핑 결과가 NaN)
        train = train.fillna(train.median(numeric_only=True)).fillna(0)

        return train, y_label

    async def introduce_myself(self, schema: LoweBoatSchema) -> LoweBoatResponse:
        query = LoweBoatQuery(id=schema.id, name=schema.name)
        return await self.repository.introduce_myself(query)

        
