from __future__ import annotations

import asyncio
import logging
import re

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from community.app.ports.output.content_filter_port import ContentFilterPort

logger = logging.getLogger(__name__)

# KcELECTRA-base(beomi/KcELECTRA-base-v2022)를 12개 유해표현 카테고리로
# 파인튜닝한 다중 라벨 분류 모델. 최초 사용 시 Hugging Face에서 자동 다운로드된다.
_FILTER_MODEL = "TTA-DQA/HateDetection_MultiLabel_KcElectra_FineTuning"

_NO_HATE_LABEL = "no_hate"
_THRESHOLD = 0.5

# LLM/모델 판정 전 확실한 비속어를 빠르게 걸러내는 스톱워드 사전 (모델이 짧은 욕설을
# 문맥 없이 정상으로 오판하는 사례가 있어, 명확한 케이스는 모델 호출 없이 즉시 차단).
_STOP_WORDS = (
    "씨발", "씨팔", "시발", "시팔", "개새끼", "개새기", "병신", "븅신", "지랄",
    "좆", "쓰레기새끼", "머저리", "미친놈", "미친년", "닥쳐", "죽여버린다", "죽여버릴",
)
_STOP_WORD_RE = re.compile("|".join(re.escape(word) for word in _STOP_WORDS))


class KcElectraContentFilterClient(ContentFilterPort):
    """스톱워드 사전 + KcELECTRA 기반 다중 라벨 혐오표현 분류 모델
    (`TTA-DQA/HateDetection_MultiLabel_KcElectra_FineTuning`)로 수신 콘텐츠를
    정상/차단 판정한다. `no_hate`를 제외한 라벨(insult/abuse/obscenity 등) 중
    하나라도 임계값을 넘으면 BLOCK으로 판정한다."""

    def __init__(self, model_name: str = _FILTER_MODEL) -> None:
        self.model_name = model_name
        self._tokenizer = AutoTokenizer.from_pretrained(model_name)
        self._model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self._model.eval()
        self._id2label = self._model.config.id2label

    async def is_normal(self, content: str) -> bool:
        if _STOP_WORD_RE.search(content):
            logger.info("[KcElectraContentFilterClient] pre-check verdict=BLOCK (stop word)")
            return False

        return await asyncio.to_thread(self._classify, content)

    def _classify(self, content: str) -> bool:
        inputs = self._tokenizer(content, return_tensors="pt", truncation=True)
        with torch.no_grad():
            logits = self._model(**inputs).logits
        probs = torch.sigmoid(logits).squeeze(0).tolist()

        blocked_labels = [
            self._id2label[i]
            for i, prob in enumerate(probs)
            if prob >= _THRESHOLD and self._id2label[i] != _NO_HATE_LABEL
        ]
        verdict = "BLOCK" if blocked_labels else "NORMAL"
        logger.info(
            "[KcElectraContentFilterClient] model=%s verdict=%s labels=%s",
            self.model_name,
            verdict,
            blocked_labels,
        )
        return not blocked_labels
