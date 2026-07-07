from __future__ import annotations

import io
import logging

import pandas as pd
from pandas import DataFrame
from titanic.adapter.inbound.api.schemas.crew_smith_captin_schemas import (
    SmithCaptainSchema,
    SmithChatRequest,
    SmithChatResponse,
)
from titanic.app.dtos.crew_smith_captin_dto import SmithCaptainQuery, SmithCaptainResponse
from titanic.app.ports.input.crew_andrews_architect_use_case import AndrewsArchitectUseCase
from titanic.app.ports.input.crew_hartley_violin_use_case import HartleyViolinUseCase
from titanic.app.ports.input.crew_lowe_boat_use_case import LoweBoatUseCase
from titanic.app.ports.input.crew_smith_captin_use_case import SmithCaptainUseCase
from titanic.app.ports.input.crew_walter_roaster_use_case import WalterRoasterUseCase
from titanic.app.ports.input.passenger_cal_tester_use_case import CalTesterUseCase
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.ports.input.passenger_rose_model_use_case import RoseModelUseCase
from titanic.app.ports.output.crew_smith_captin_port import SmithCaptainPort

logger = logging.getLogger(__name__)

_PCLASS_KEYWORDS = {
    "1등석": 1, "1등급": 1, "일등석": 1, "일등급": 1,
    "2등석": 2, "2등급": 2, "이등석": 2, "이등급": 2,
    "3등석": 3, "3등급": 3, "삼등석": 3, "삼등급": 3,
}
_COUNT_CUE_KEYWORDS = ("몇명", "명수", "비율", "총원", "총")
# Kaggle 타이타닉 공식 분할: train 891명 + test 418명. DB에는 train만 적재돼 있어
# test_set이 비어 있더라도 "총 인원"은 공식 데이터셋 기준 고정값으로 답한다.
_KAGGLE_OFFICIAL_TOTAL_PASSENGERS = 1309


class SmithCaptainInteractor(SmithCaptainUseCase):

    def __init__(
        self,
        repository: SmithCaptainPort,
        andrews: AndrewsArchitectUseCase,
        jack: JackTrainerUseCase,
        rose: RoseModelUseCase,
        cal: CalTesterUseCase,
        walter: WalterRoasterUseCase,
        lowe: LoweBoatUseCase,
        hartley: HartleyViolinUseCase,
    ) -> None:
        self.repository = repository
        self.andrews = andrews
        self.jack = jack
        self.rose = rose
        self.cal = cal
        self.walter = walter
        self.lowe = lowe
        self.hartley = hartley

    async def chat(self, schema: SmithChatRequest) -> SmithChatResponse:
        train_set: DataFrame = await self.walter.get_train_set()
        test_set: DataFrame = await self.walter.get_test_set()
        featured_set, y_label = self.lowe.feature_engineering(train_set)
        correlation_plot: io.BytesIO = self.hartley.generate_correlation_plot(train_set)
        trained_set = await self.jack.train_model(train_set)
        # cal.test_model은 jack.train_model의 80/20 검증 점수로 순위를 매기므로
        # Survived 라벨이 없는 test_set이 아니라 train_set을 넘긴다
        tested_set = await self.cal.test_model(train_set)
        intent_result = self.andrews.analyze_intent(schema.message)
        intent = intent_result["intent"]
        # 나이/성별 추출은 정규식 기반이라 Kiwi 형태소 분석(짧은 문장에서 애매해질 수 있음)보다 안정적 —
        # 프로필이 잡히면 의도 분류 결과와 무관하게 예측을 우선한다
        profile = self.andrews.extract_passenger_profile(schema.message)

        if profile:
            reply = self._build_prediction_reply(profile)
        elif intent == "MODEL_TRAIN":
            reply = self._build_ranking_reply(tested_set)
        elif intent in ("STATISTICS", "SURVIVAL_PREDICT"):
            reply = self._build_statistics_reply(schema.message, train_set, test_set)
        else:
            reply = f"감지된 의도: {intent} (키워드: {', '.join(intent_result['keywords']) or '없음'})"

        logger.info("[SmithCaptainInteractor] chat | intent=%s", intent)

        return SmithChatResponse(reply=reply, model="andrews-kiwi")

    def _build_statistics_reply(self, message: str, train_set: DataFrame, test_set: DataFrame) -> str:
        if any(keyword in message for keyword in _COUNT_CUE_KEYWORDS):
            combined = pd.concat([train_set, test_set], ignore_index=True)

            for keyword, pclass in _PCLASS_KEYWORDS.items():
                if keyword in message:
                    return self._count_by_pclass_reply(combined, pclass)

            if any(keyword in message for keyword in ("남자", "여자", "성별")):
                return self._count_by_gender_reply(combined)

            if any(keyword in message for keyword in ("생존", "사망")):
                return self._count_by_survived_reply(train_set)

            return f"타이타닉 데이터셋(Kaggle 공식 train/test 분할 기준) 총 탑승객은 {_KAGGLE_OFFICIAL_TOTAL_PASSENGERS:,}명입니다."

        ranking = self.hartley.get_survived_correlation_ranking(train_set)
        lines = [f"{i}. {name}({corr:+.2f})" for i, (name, corr) in enumerate(ranking, start=1)]
        return "생존율과 상관관계가 높은 순서: " + ", ".join(lines)

    def _count_by_pclass_reply(self, combined: DataFrame, pclass: int) -> str:
        pclass_numeric = pd.to_numeric(combined["Pclass"], errors="coerce")
        count = int((pclass_numeric == pclass).sum())
        return f"{pclass}등석에는 총 {count}명이 탑승했습니다."

    def _count_by_gender_reply(self, combined: DataFrame) -> str:
        gender = combined["gender"].astype(str).str.lower()
        male = int((gender == "male").sum())
        female = int((gender == "female").sum())
        total = male + female
        if total == 0:
            return "성별 데이터를 찾을 수 없습니다."
        return (
            f"남성 {male}명({male / total * 100:.1f}%), "
            f"여성 {female}명({female / total * 100:.1f}%)이 탑승했습니다."
        )

    def _count_by_survived_reply(self, train_set: DataFrame) -> str:
        survived_numeric = pd.to_numeric(train_set["Survived"], errors="coerce").fillna(0)
        total = len(train_set)
        survived = int(survived_numeric.sum())
        died = total - survived
        return (
            f"생존 기록이 있는 {total}명 중 생존자 {survived}명({survived / total * 100:.1f}%), "
            f"사망자 {died}명({died / total * 100:.1f}%)입니다."
        )

    def _build_prediction_reply(self, profile: dict) -> str:
        result = self.jack.predict_survival(profile)

        profile_desc = []
        if "Age" in profile:
            profile_desc.append(f"{int(profile['Age'])}세")
        profile_desc.append("여성" if profile.get("gender") == 1 else "남성" if profile.get("gender") == 0 else None)
        desc = " ".join(part for part in profile_desc if part) or "해당 조건의 승객"

        verdict = "생존했을 것" if result["survived"] else "생존하지 못했을 것"
        return (
            f"{desc} 승객은 {verdict}으로 예측됩니다 "
            f"(생존 확률 약 {result['probability'] * 100:.0f}%, 모델: {result['model']})."
        )

    def _build_ranking_reply(self, tested_set: dict) -> str:
        winner = tested_set["winner"]
        accuracy = next(
            (entry["accuracy"] for entry in tested_set["ranking"] if entry["model"] == winner),
            None,
        )
        if accuracy is None:
            return f"학습된 모델 중 1위는 {winner}입니다."
        return f"학습된 모델 중 1위는 {winner}이며, 검증 정확도는 {accuracy * 100:.1f}%입니다."

    async def introduce_myself(self, schema: SmithCaptainSchema) -> SmithCaptainResponse:
        '''스미스 선장의 자기소개 인터렉트'''
        return await self.repository.introduce_myself(SmithCaptainQuery(
            id=schema.id,
            name=schema.name,
        ))
