"""문제 정의·컬럼 메타 — secom의 user_schemas와 유사한 스키마 층."""

from __future__ import annotations

from pydantic import BaseModel, Field

TITANIC_PROBLEM_SUMMARY = (
    "타이타닉 탑승자 명단을 사용한 데이터 분석 및 생존자 예측. "
    "1912년 4월 10일 Southampton 출발, 4월 15일 침몰. "
    "이진 분류: Survived 1=생존, 0=사망. "
    "주요 독립변수 후보: Pclass, Sex, Age, SibSp, Parch, Fare, Embarked 등으로 생존 여부 예측."
)

TITANIC_COLUMN_DESCRIPTIONS: dict[str, str] = {
    "PassengerId": "승객 식별자",
    "Survived": "생존 여부 (0=사망, 1=생존) — 타깃",
    "Pclass": "티켓 등급 (1=1등석, 2=2등석, 3=3등석)",
    "Name": "이름",
    "Sex": "성별",
    "Age": "나이",
    "SibSp": "함께 탑승한 형제·배우자 수",
    "Parch": "함께 탑승한 부모·자녀 수",
    "Ticket": "티켓 번호",
    "Fare": "탑승 요금",
    "Cabin": "객실 번호(없을 수 있음)",
    "Embarked": "승선 항구 (C=Cherbourg, Q=Queenstown, S=Southampton)",
    "Boat": "탈출 보트 번호(해당 컬럼이 있는 데이터셋에서만)",
}


class TitanicProblemDefinition(BaseModel):
    """문제 정의(문서·API 응답용)."""

    title: str = Field(default="타이타닉 생존자 예측")
    summary: str = Field(default=TITANIC_PROBLEM_SUMMARY)
    target_variable: str = Field(default="Survived")
    task_type: str = Field(default="binary_classification")


class TitanicColumnDoc(BaseModel):
    """단일 컬럼 설명."""

    name: str
    description: str


class TitanicDatasetSchemaHint(BaseModel):
    """데이터셋 스키마 힌트(교육용)."""

    columns: list[TitanicColumnDoc] = Field(
        default_factory=lambda: [
            TitanicColumnDoc(name=k, description=v)
            for k, v in TITANIC_COLUMN_DESCRIPTIONS.items()
        ]
    )
