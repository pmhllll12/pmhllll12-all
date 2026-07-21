from __future__ import annotations

import io
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from ontology.adapter.inbound.api.v1.image_classifier_router import image_classifier_router
from ontology.app.dtos.image_classifier_dto import ClassifyImageResult, LabelScore
from ontology.app.ports.input.image_classifier_use_case import ImageClassifierUseCase
from ontology.dependencies.image_classifier_provider import get_image_classifier_use_case
from PIL import Image

_MODEL_PATH = Path(__file__).resolve().parents[5] / "models" / "convnext_nano.onnx"
_HAS_MODEL = _MODEL_PATH.is_file()
_SKIP_REASON = "convnext_nano.onnx가 없음 — scripts/export_onnx.py 먼저 실행 필요"


def _jpeg_bytes(color: tuple[int, int, int] = (10, 200, 10)) -> bytes:
    image = Image.new("RGB", (64, 64), color=color)
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


def _make_app() -> FastAPI:
    app = FastAPI()
    app.include_router(image_classifier_router, prefix="/api/vision")
    return app


class _StubUseCase(ImageClassifierUseCase):
    """실제 ONNX 모델 없이 라우터 자체(검증·에러 매핑·응답 스키마)만 테스트하기 위한 스텁."""

    async def classify(self, command) -> ClassifyImageResult:  # noqa: ANN001
        return ClassifyImageResult(
            ok=True,
            label="tabby cat",
            confidence=0.83,
            top5=[LabelScore(label="tabby cat", confidence=0.83)],
            uncertain=False,
            inference_ms=1.2,
        )


def test_classify_rejects_non_image_content_type():
    app = _make_app()
    client = TestClient(app)
    response = client.post(
        "/api/vision/classify",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 422


def test_classify_rejects_empty_file():
    app = _make_app()
    client = TestClient(app)
    response = client.post(
        "/api/vision/classify",
        files={"file": ("empty.jpg", b"", "image/jpeg")},
    )
    assert response.status_code == 422


def test_classify_with_stub_use_case_returns_expected_shape():
    app = _make_app()
    app.dependency_overrides[get_image_classifier_use_case] = lambda: _StubUseCase()
    client = TestClient(app)

    response = client.post(
        "/api/vision/classify",
        files={"file": ("cat.jpg", _jpeg_bytes(), "image/jpeg")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["label"] == "tabby cat"
    assert body["confidence"] == pytest.approx(0.83)
    assert body["uncertain"] is False
    assert body["top5"][0]["label"] == "tabby cat"


@pytest.mark.skipif(not _HAS_MODEL, reason=_SKIP_REASON)
def test_classify_end_to_end_with_real_model():
    app = _make_app()
    client = TestClient(app)

    response = client.post(
        "/api/vision/classify",
        files={"file": ("solid.jpg", _jpeg_bytes(), "image/jpeg")},
    )

    assert response.status_code == 200
    body = response.json()
    assert 0.0 <= body["confidence"] <= 1.0
    assert len(body["top5"]) == 5
