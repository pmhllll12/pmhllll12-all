from __future__ import annotations

import logging
import re
from typing import Any

from kiwipiepy import Kiwi
from titanic.adapter.inbound.api.schemas.crew_andrews_architect_schemas import (
    AndrewsArchitectSchema,
)
from titanic.app.constants.intent_map import INTENT_MAP
from titanic.app.dtos.crew_andrews_architect_dto import (
    AndrewsArchitectQuery,
    AndrewsArchitectResponse,
)
from titanic.app.ports.input.crew_andrews_architect_use_case import AndrewsArchitectUseCase
from titanic.app.ports.output.crew_andrews_architect_port import AndrewsArchitectPort

logger = logging.getLogger(__name__)

_AGE_PATTERN = re.compile(r"(\d{1,3})\s*(?:세|살)")
_FEMALE_KEYWORDS = ("여자", "여성", "소녀", "female", "woman")
_MALE_KEYWORDS = ("남자", "남성", "소년", "male", "man")
# "남자 여자 명수랑 비율 알려줘"처럼 집계를 묻는 문장은 한 명의 가상 승객 프로필이 아니므로 제외
_STATISTICS_OVERRIDE_KEYWORDS = ("몇명", "명수", "비율", "통계", "분포", "총원", "전체", "합계", "평균")


class AndrewsArchitectInteractor(AndrewsArchitectUseCase):

    def __init__(self, repository: AndrewsArchitectPort):
        self.repository = repository
        self.kiwi = Kiwi()

    def analyze_intent(self, messages: str) -> dict[str, Any]:
        '''Kiwi 형태소 분석으로 프론트 질문의 의도를 파악하는 메소드

        반환값:
            intent   : 감지된 의도 (SURVIVAL_PREDICT / STATISTICS / PASSENGER_SEARCH / MODEL_TRAIN / UNKNOWN)
            keywords : 분석에 사용된 핵심 형태소 목록
            scores   : 의도별 매칭 점수
            tokens   : Kiwi가 분석한 전체 (형태소, 품사) 쌍 목록
        '''
        # 명사(NN*), 동사 어간(VV/VA), 파생어근(XR)만 의도 판별에 사용
        tokens = self.kiwi.tokenize(messages)
        keywords = [t.form for t in tokens if t.tag.startswith(("NN", "VV", "VA", "XR"))]

        scores: dict[str, int] = {intent: 0 for intent in INTENT_MAP}
        for keyword in keywords:
            for intent, kw_set in INTENT_MAP.items():
                if keyword in kw_set:
                    scores[intent] += 1

        best_intent = max(scores, key=lambda k: scores[k])
        intent = best_intent if scores[best_intent] > 0 else "UNKNOWN"

        logger.info(
            f"[AndrewsArchitectInteractor] analyze_intent | messages={messages!r} "
            f"intent={intent} scores={scores}"
        )
        return {
            "intent": intent,
            "keywords": keywords,
            "scores": scores,
            "tokens": [(t.form, str(t.tag)) for t in tokens],
        }

    def extract_passenger_profile(self, message: str) -> dict[str, Any]:
        '''생존 예측 질의 문장에서 나이·성별 등 승객 프로필을 추출 (예: "33세 남자" → {"Age": 33.0, "gender": 0})

        "명수/비율" 등 집계를 묻는 문장은 가상의 한 승객을 가리키는 게 아니므로 빈 dict를 반환한다.
        '''
        if any(keyword in message for keyword in _STATISTICS_OVERRIDE_KEYWORDS):
            return {}

        profile: dict[str, Any] = {}

        age_match = _AGE_PATTERN.search(message)
        if age_match:
            profile["Age"] = float(age_match.group(1))

        lowered = message.lower()
        if any(keyword in message for keyword in _FEMALE_KEYWORDS) or any(keyword in lowered for keyword in ("female", "woman")):
            profile["gender"] = 1
        elif any(keyword in message for keyword in _MALE_KEYWORDS) or any(keyword in lowered for keyword in ("male", "man")):
            profile["gender"] = 0

        return profile

    async def introduce_myself(self, schema: AndrewsArchitectSchema) -> AndrewsArchitectResponse:
        '''앤드류 설계자의 자기소개 인터렉트'''

        return await self.repository.introduce_myself(AndrewsArchitectQuery(
            id = schema.id,
            name = schema.name
        ))