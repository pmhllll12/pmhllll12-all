from __future__ import annotations

import asyncio
import io
from pathlib import Path

import numpy as np
import pytest
from ontology.app.dtos.image_classifier_dto import ClassifyImageCommand
from ontology.app.ports.output.image_classifier_model_port import ImageClassifierModelPort
from ontology.app.use_cases.image_classifier_interactor import (
    ImageClassifierInteractor,
    InvalidImageError,
)
from PIL import Image

_MODEL_PATH = Path(__file__).resolve().parents[3] / "models" / "convnext_nano.onnx"
_HAS_MODEL = _MODEL_PATH.is_file()
_SKIP_REASON = "convnext_nano.onnx가 없음 — scripts/export_onnx.py 먼저 실행 필요"


class _StubModelPort(ImageClassifierModelPort):
    def __init__(self, model_path: Path = _MODEL_PATH) -> None:
        self.model_path = model_path

    def get_model_path(self) -> str:
        return str(self.model_path)


def _make_interactor() -> ImageClassifierInteractor:
    return ImageClassifierInteractor(model_port=_StubModelPort())


def _synthetic_jpeg(color: tuple[int, int, int], size: int = 256, seed: int | None = None) -> bytes:
    """외부 샘플 파일 의존 없이(라이선스·경로 문제 회피) 결정적인 테스트용 이미지를 만든다."""
    if seed is not None:
        rng = np.random.default_rng(seed)
        array = rng.integers(0, 256, size=(size, size, 3), dtype=np.uint8)
        image = Image.fromarray(array, mode="RGB")
    else:
        image = Image.new("RGB", (size, size), color=color)
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


def test_softmax_sums_to_one_and_preserves_ranking():
    logits = np.array([2.0, 1.0, 0.1])
    probs = ImageClassifierInteractor._softmax(logits)
    assert probs.sum() == pytest.approx(1.0, abs=1e-6)
    assert probs[0] > probs[1] > probs[2]


def test_classify_rejects_empty_content():
    async def _run():
        interactor = _make_interactor()
        with pytest.raises(InvalidImageError):
            await interactor.classify(ClassifyImageCommand(content=b"", filename="empty.jpg"))

    asyncio.run(_run())


def test_classify_rejects_corrupted_image():
    async def _run():
        interactor = _make_interactor()
        with pytest.raises(InvalidImageError):
            await interactor.classify(
                ClassifyImageCommand(content=b"not an image", filename="broken.jpg")
            )

    asyncio.run(_run())


@pytest.mark.skipif(not _HAS_MODEL, reason=_SKIP_REASON)
def test_classify_real_model_returns_well_formed_top5():
    async def _run():
        interactor = _make_interactor()
        content = _synthetic_jpeg(color=(30, 120, 30))
        return await interactor.classify(
            ClassifyImageCommand(content=content, filename="solid_green.jpg")
        )

    result = asyncio.run(_run())
    assert result.ok is True
    assert len(result.top5) == 5
    assert result.label == result.top5[0].label
    assert result.confidence == pytest.approx(result.top5[0].confidence)
    # confidence는 softmax 출력이라 항상 [0, 1] 범위 — top5는 내림차순 정렬이어야 한다.
    confidences = [item.confidence for item in result.top5]
    assert confidences == sorted(confidences, reverse=True)
    assert all(0.0 <= c <= 1.0 for c in confidences)
    assert result.inference_ms > 0


@pytest.mark.skipif(not _HAS_MODEL, reason=_SKIP_REASON)
def test_classify_uncertain_flag_reflects_threshold():
    async def _run():
        interactor = _make_interactor()
        # 순수 랜덤 노이즈 이미지 — ImageNet 어떤 클래스에도 강하게 대응하지 않아
        # top-1 confidence가 거의 항상 낮게 나온다.
        content = _synthetic_jpeg(color=(0, 0, 0), seed=42)
        below_threshold = await interactor.classify(
            ClassifyImageCommand(content=content, filename="noise.jpg", confidence_threshold=0.99)
        )
        above_threshold = await interactor.classify(
            ClassifyImageCommand(content=content, filename="noise.jpg", confidence_threshold=0.0)
        )
        return below_threshold, above_threshold

    below_threshold, above_threshold = asyncio.run(_run())
    assert below_threshold.uncertain is True
    assert above_threshold.uncertain is False


@pytest.mark.skipif(not _HAS_MODEL, reason=_SKIP_REASON)
def test_classify_is_deterministic_for_same_input():
    async def _run():
        interactor = _make_interactor()
        content = _synthetic_jpeg(color=(200, 50, 50))
        first = await interactor.classify(ClassifyImageCommand(content=content))
        second = await interactor.classify(ClassifyImageCommand(content=content))
        return first, second

    first, second = asyncio.run(_run())
    assert first.label == second.label
    assert first.confidence == pytest.approx(second.confidence)
