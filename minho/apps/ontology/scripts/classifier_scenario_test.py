#!/usr/bin/env python3
"""이미지 분류 파이프라인을 다양한 시나리오(정상/애매/손상)로 훑어보는 스모크 테스트.

pytest 유닛 테스트와 달리 사람이 눈으로 결과를 확인하기 위한 스크립트다.
외부 샘플 파일에 의존하지 않도록(라이선스·경로 문제 회피) 대부분 합성 이미지를
쓰고, 로컬에 ultralytics 샘플이 있으면 보너스로 같이 돌린다.

실행:
    python apps/ontology/scripts/classifier_scenario_test.py
"""

from __future__ import annotations

import asyncio
import io
import logging
import sys
from pathlib import Path

import numpy as np

_ONTOLOGY_ROOT = Path(__file__).resolve().parents[1]
_APPS_ROOT = _ONTOLOGY_ROOT.parent
if str(_APPS_ROOT) not in sys.path:
    sys.path.insert(0, str(_APPS_ROOT))

logging.basicConfig(level=logging.WARNING)  # 시나리오 결과만 보이게 인터랙터 로그는 줄인다

from ontology.adapter.outbound.resource_adapters.onnx.image_classifier_model_adapter import (  # noqa: E402
    LocalImageClassifierModelAdapter,
)
from ontology.app.dtos.image_classifier_dto import ClassifyImageCommand  # noqa: E402
from ontology.app.use_cases.image_classifier_interactor import (  # noqa: E402
    ImageClassifierInteractor,
    InvalidImageError,
)
from PIL import Image  # noqa: E402


def _solid(color: tuple[int, int, int]) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (256, 256), color=color).save(buf, format="JPEG")
    return buf.getvalue()


def _gradient() -> bytes:
    array = np.zeros((256, 256, 3), dtype=np.uint8)
    for x in range(256):
        array[:, x, 0] = x
        array[:, x, 2] = 255 - x
    buf = io.BytesIO()
    Image.fromarray(array, mode="RGB").save(buf, format="JPEG")
    return buf.getvalue()


def _checkerboard() -> bytes:
    array = np.zeros((256, 256, 3), dtype=np.uint8)
    for y in range(0, 256, 32):
        for x in range(0, 256, 32):
            if (x // 32 + y // 32) % 2 == 0:
                array[y : y + 32, x : x + 32] = 255
    buf = io.BytesIO()
    Image.fromarray(array, mode="RGB").save(buf, format="JPEG")
    return buf.getvalue()


def _noise(seed: int) -> bytes:
    rng = np.random.default_rng(seed)
    array = rng.integers(0, 256, size=(256, 256, 3), dtype=np.uint8)
    buf = io.BytesIO()
    Image.fromarray(array, mode="RGB").save(buf, format="JPEG")
    return buf.getvalue()


# (표시 이름, 이미지 바이트 생성 함수 또는 None(손상 케이스), 기대 카테고리)
_SCENARIOS: list[tuple[str, bytes | None, str]] = [
    ("단색 빨강", _solid((220, 30, 30)), "정상"),
    ("단색 초록", _solid((30, 200, 30)), "정상"),
    ("단색 파랑", _solid((30, 30, 220)), "정상"),
    ("단색 검정", _solid((10, 10, 10)), "정상"),
    ("단색 흰색", _solid((245, 245, 245)), "정상"),
    ("좌우 그라디언트", _gradient(), "애매"),
    ("체커보드 패턴", _checkerboard(), "애매"),
    ("랜덤 노이즈 #1", _noise(1), "애매"),
    ("랜덤 노이즈 #2", _noise(2), "애매"),
    ("랜덤 노이즈 #3", _noise(3), "애매"),
    ("빈 파일", b"", "손상"),
    ("텍스트를 이미지로 위장", b"this is not an image at all", "손상"),
    ("잘린(truncated) JPEG", _solid((100, 100, 100))[:50], "손상"),
]


async def _run_one(
    interactor: ImageClassifierInteractor, name: str, content: bytes, expect: str
) -> None:
    try:
        result = await interactor.classify(ClassifyImageCommand(content=content, filename=name))
    except InvalidImageError as exc:
        status = "OK(예상대로 거부)" if expect == "손상" else "FAIL(거부되면 안 되는데 거부됨)"
        print(f"[{status}] {name:<24s} -> InvalidImageError: {exc}")
        return

    if expect == "손상":
        print(f"[FAIL(거부돼야 하는데 통과됨)] {name:<24s} -> {result.label}")
        return

    flag = "uncertain" if result.uncertain else "confident"
    print(
        f"[OK] {name:<24s} -> {result.label:<30s} "
        f"conf={result.confidence:.3f} ({flag}) {result.inference_ms:.1f}ms"
    )


async def main() -> None:
    interactor = ImageClassifierInteractor(model_port=LocalImageClassifierModelAdapter())

    print(f"=== 합성 시나리오 {len(_SCENARIOS)}건 ===")
    for name, content, expect in _SCENARIOS:
        await _run_one(interactor, name, content, expect)

    # 로컬에 ultralytics가 설치돼 있으면(개발 환경) 보너스로 실제 사진도 같이 확인한다.
    try:
        from ultralytics.utils import ASSETS

        print("\n=== 보너스: 로컬 ultralytics 샘플 사진 ===")
        for image_path in sorted(Path(ASSETS).glob("*.jpg")):
            await _run_one(interactor, image_path.name, image_path.read_bytes(), "정상")
    except ImportError:
        pass


if __name__ == "__main__":
    asyncio.run(main())
