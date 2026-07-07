"""수업용 문제 정의·데이터 컬럼 설명 (GET /titanic/problem)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ColumnHint(BaseModel):
    name: str
    dtype: str
    description: str


class TitanicDatasetSchemaHint(BaseModel):
    """Kaggle Titanic-style CSV 컬럼 안내."""

    columns: list[ColumnHint] = Field(
        default_factory=lambda: [
            ColumnHint(
                name="PassengerId",
                dtype="int",
                description="승객 식별자 (행 번호에 가깝게 사용)",
            ),
            ColumnHint(
                name="Survived",
                dtype="int (0/1)",
                description="생존 여부. 1=생존, 0=사망 (예측 타깃)",
            ),
            ColumnHint(
                name="Pclass",
                dtype="int",
                description="티켓 등급 1=1등석, 2=2등석, 3=3등석",
            ),
            ColumnHint(name="Name", dtype="str", description="이름 (호칭·성별 단서 포함)"),
            ColumnHint(name="Sex", dtype="str", description="male / female"),
            ColumnHint(name="Age", dtype="float", description="나이 (결측 가능)"),
            ColumnHint(name="SibSp", dtype="int", description="형제·배우자 동승 수"),
            ColumnHint(name="Parch", dtype="int", description="부모·자녀 동승 수"),
            ColumnHint(name="Ticket", dtype="str", description="티켓 번호"),
            ColumnHint(name="Fare", dtype="float", description="운임"),
            ColumnHint(name="Cabin", dtype="str", description="객실 번호 (결측 많음)"),
            ColumnHint(
                name="Embarked",
                dtype="str",
                description="승선 항구 코드 (C=Cherbourg, Q=Queenstown, S=Southampton)",
            ),
        ]
    )
    notes: str = (
        "API는 저장소 내부 CSV 없이 메모리 데모 프레임으로 동일 스키마를 안내합니다. "
        "실제 수업 데이터는 업로드·DB 등 외부 소스에서 연동하세요."
    )


class TitanicProblemDefinition(BaseModel):
    title: str = "Titanic 생존 예측 (이진 분류)"
    objective: str = (
        "승객 정보를 바탕으로 Survived(생존 여부)를 예측하는 모델을 학습·평가합니다."
    )
    target_column: str = "Survived"
    task_type: str = "binary_classification"
    suggested_models: list[str] = Field(
        default_factory=lambda: [
            "DecisionTreeClassifier",
            "LogisticRegression",
            "RandomForestClassifier",
        ]
    )
