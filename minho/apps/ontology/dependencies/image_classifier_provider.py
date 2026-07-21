from __future__ import annotations

from ontology.adapter.outbound.resource_adapters.onnx.image_classifier_model_adapter import (
    LocalImageClassifierModelAdapter,
)
from ontology.app.ports.input.image_classifier_use_case import ImageClassifierUseCase
from ontology.app.ports.output.image_classifier_model_port import ImageClassifierModelPort
from ontology.app.use_cases.image_classifier_interactor import ImageClassifierInteractor

# 다른 provider들과 달리 요청마다 새로 만들지 않고 모듈 전역에 캐시한다: ONNX 세션
# 로딩(+ CUDA 컨텍스트 초기화)이 요청당 수백ms~1s대라 매 요청 재생성하면 응답이 느려진다.
_classifier_use_case: ImageClassifierUseCase | None = None


def get_image_classifier_model_port() -> ImageClassifierModelPort:
    return LocalImageClassifierModelAdapter()


def get_image_classifier_use_case() -> ImageClassifierUseCase:
    global _classifier_use_case
    if _classifier_use_case is None:
        _classifier_use_case = ImageClassifierInteractor(
            model_port=get_image_classifier_model_port()
        )
    return _classifier_use_case
