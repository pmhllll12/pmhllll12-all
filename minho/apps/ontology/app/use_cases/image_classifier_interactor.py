from __future__ import annotations

import logging
import time
from pathlib import Path

import numpy as np
import onnxruntime as ort
from ontology.app.dtos.image_classifier_dto import (
    ClassifyImageCommand,
    ClassifyImageResult,
    LabelScore,
)
from ontology.app.ports.input.image_classifier_use_case import ImageClassifierUseCase
from ontology.app.ports.output.image_classifier_model_port import ImageClassifierModelPort
from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)

_TOP_K = 5

# scripts/export_onnx.py에서 ONNX로 변환한 모델과 동일한 timm 태그.
# 여기서는 가중치를 내려받지 않고(pretrained=False) 전처리 설정(mean/std/input_size 등)만
# 얻는 용도로만 쓴다 — 실제 추론은 ONNX Runtime 세션이 담당한다.
_MODEL_TAG = "convnext_nano.in12k_ft_in1k"


class InvalidImageError(ValueError):
    """분류 대상 이미지가 비어있거나 손상되어 디코딩할 수 없을 때 발생한다."""


class ImageClassifierInteractor(ImageClassifierUseCase):
    def __init__(self, model_port: ImageClassifierModelPort) -> None:
        self.model_port = model_port
        self._session: ort.InferenceSession | None = None
        self._input_name: str | None = None
        self._transform = None
        self._labels: list[str] | None = None

    def _get_session(self) -> ort.InferenceSession:
        if self._session is None:
            model_path = self.model_port.get_model_path()
            available = ort.get_available_providers()
            providers = (
                ["CUDAExecutionProvider", "CPUExecutionProvider"]
                if "CUDAExecutionProvider" in available
                else ["CPUExecutionProvider"]
            )
            self._session = ort.InferenceSession(model_path, providers=providers)
            self._input_name = self._session.get_inputs()[0].name
            logger.info(
                "[ImageClassifierInteractor] 모델 로드 완료 model_path=%r providers=%r",
                model_path,
                self._session.get_providers(),
            )
        return self._session

    def _get_transform(self):
        if self._transform is None:
            import timm
            from timm.data import create_transform, resolve_data_config

            # pretrained=False: 가중치는 내려받지 않고 모델 아키텍처에 딸린
            # 전처리 설정(mean/std/input_size/interpolation)만 조회한다.
            reference_model = timm.create_model(_MODEL_TAG, pretrained=False)
            data_config = resolve_data_config({}, model=reference_model)
            self._transform = create_transform(**data_config)
            logger.info("[ImageClassifierInteractor] 전처리 설정 로드 완료 config=%r", data_config)
        return self._transform

    def _get_labels(self) -> list[str]:
        if self._labels is None:
            from timm.data import ImageNetInfo

            info = ImageNetInfo()
            self._labels = [info.index_to_description(i) for i in range(info.num_classes())]
        return self._labels

    def _preprocess(self, image_path: str) -> np.ndarray:
        path = Path(image_path)
        if not path.is_file() or path.stat().st_size == 0:
            raise InvalidImageError(f"이미지 파일이 비어있거나 존재하지 않습니다: {image_path}")
        try:
            image = Image.open(path)
            image.load()
            image = image.convert("RGB")
        except (UnidentifiedImageError, OSError) as exc:
            raise InvalidImageError(
                f"이미지를 디코딩할 수 없습니다(손상된 파일): {image_path}"
            ) from exc

        transform = self._get_transform()
        tensor = transform(image).unsqueeze(0)  # (1, C, H, W)
        return tensor.numpy().astype(np.float32)

    @staticmethod
    def _softmax(logits: np.ndarray) -> np.ndarray:
        shifted = logits - logits.max()
        exp = np.exp(shifted)
        return exp / exp.sum()

    def classify(self, command: ClassifyImageCommand) -> ClassifyImageResult:
        session = self._get_session()
        input_tensor = self._preprocess(command.image_path)

        started = time.perf_counter()
        outputs = session.run(None, {self._input_name: input_tensor})
        elapsed_ms = (time.perf_counter() - started) * 1000

        probs = self._softmax(outputs[0][0])
        labels = self._get_labels()
        top_indices = np.argsort(probs)[::-1][:_TOP_K]
        top5 = [LabelScore(label=labels[i], confidence=float(probs[i])) for i in top_indices]

        best = top5[0]
        uncertain = best.confidence < command.confidence_threshold

        logger.info(
            "[ImageClassifierInteractor] classify image_path=%r label=%r confidence=%.4f "
            "uncertain=%s elapsed_ms=%.1f provider=%s",
            command.image_path,
            best.label,
            best.confidence,
            uncertain,
            elapsed_ms,
            session.get_providers()[0],
        )

        return ClassifyImageResult(
            ok=True,
            label=best.label,
            confidence=best.confidence,
            top5=top5,
            uncertain=uncertain,
            inference_ms=elapsed_ms,
        )
