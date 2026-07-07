from __future__ import annotations

import io
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # FastAPI 스레드풀(메인 스레드 아님)에서 그려서 GUI 백엔드 사용 시 불안정/크래시 위험
import matplotlib.pyplot as plt
import seaborn as sns
from pandas import DataFrame, factorize
from titanic.adapter.inbound.api.schemas.crew_hartley_violin_schemas import HartleyViolinSchema
from titanic.app.dtos.crew_hartley_violin_dto import HartleyViolinQuery, HartleyViolinResponse
from titanic.app.ports.input.crew_hartley_violin_use_case import HartleyViolinUseCase
from titanic.app.ports.output.crew_hartley_violin_port import HartleyViolinPort

_PLOT_OUTPUT_DIR = Path(__file__).resolve().parents[2] / "_generated" / "plots"

# domain/value_objects 파일명과 맞춘 라벨 (나머지 컬럼은 파일명과 이미 동일)
# sex_vo.py 가 gender_vo.py 로 대체됨 → Sex/gender 컬럼을 Gender 로 표기
# (CSV 원본은 "Sex", DB 경로는 walter_repository가 소문자 "gender"로 내려줌 — 둘 다 처리)
_VO_COLUMN_LABELS = {
    "Sex": "Gender",
    "gender": "Gender",
}

# Survived와 상관관계가 낮아 VO를 삭제한 Age/Title/Ticket/SibSp/Parch는 제외하고,
# 남아 있는 도메인 VO(gender_vo, pclass_vo, fare_vo, cabin_vo, embarked_vo, survived_vo)에 대응하는 컬럼만 사용
_VO_FEATURE_COLUMNS = ["Survived", "Pclass", "Gender", "Fare", "Cabin", "Embarked"]


class HartleyViolinInteractor(HartleyViolinUseCase):
    def __init__(self, repository: HartleyViolinPort) -> None:
        self.repository = repository

    async def introduce_myself(self, schema: HartleyViolinSchema) -> HartleyViolinResponse:
        query = HartleyViolinQuery(id=schema.id, name=schema.name)
        return await self.repository.introduce_myself(query)

    def _build_correlation_matrix(self, dataset: DataFrame) -> DataFrame:
        encoded_df = dataset.copy()
        for column in encoded_df.select_dtypes(include=["object"]).columns:
            encoded_df[column] = factorize(encoded_df[column])[0]
        encoded_df = encoded_df.rename(columns=_VO_COLUMN_LABELS)
        return encoded_df[_VO_FEATURE_COLUMNS].corr()

    def get_survived_correlation_ranking(self, dataset: DataFrame) -> list[tuple[str, float]]:
        '''Survived와의 상관계수를 절댓값 내림차순으로 반환 (Survived 자신은 제외)'''
        survived_corr = self._build_correlation_matrix(dataset)["Survived"].drop("Survived")
        ranked = survived_corr.reindex(survived_corr.abs().sort_values(ascending=False).index)
        return list(ranked.items())

    def generate_correlation_plot(self, dataset: DataFrame) -> io.BytesIO:
        corr = self._build_correlation_matrix(dataset)

        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
        ax.set_title("Titanic Feature Correlation including Survived")

        _PLOT_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        fig.savefig(_PLOT_OUTPUT_DIR / "correlation_plot.png", bbox_inches="tight")

        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        plt.close(fig)

        return buf
