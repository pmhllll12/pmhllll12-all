#!/usr/bin/env python3
"""ImageClassifierInteractor를 FastAPI 없이 단독 실행해 top-5 라벨/신뢰도를 출력한다.

실행:
    python apps/ontology/scripts/run_classifier_sample.py <이미지 경로>
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_ONTOLOGY_ROOT = Path(__file__).resolve().parents[1]
_APPS_ROOT = _ONTOLOGY_ROOT.parent
if str(_APPS_ROOT) not in sys.path:
    sys.path.insert(0, str(_APPS_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

from ontology.adapter.outbound.resource_adapters.onnx.image_classifier_model_adapter import (  # noqa: E402
    LocalImageClassifierModelAdapter,
)
from ontology.app.dtos.image_classifier_dto import ClassifyImageCommand  # noqa: E402
from ontology.app.use_cases.image_classifier_interactor import (  # noqa: E402
    ImageClassifierInteractor,
    InvalidImageError,
)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"사용법: {sys.argv[0]} <이미지 경로>", file=sys.stderr)
        return 2

    image_path = sys.argv[1]
    interactor = ImageClassifierInteractor(model_port=LocalImageClassifierModelAdapter())

    try:
        result = interactor.classify(ClassifyImageCommand(image_path=image_path))
    except (InvalidImageError, FileNotFoundError) as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 1

    print(
        f"\n최상위 예측: {result.label} "
        f"(confidence={result.confidence:.4f}, uncertain={result.uncertain})"
    )
    print(f"추론 소요 시간: {result.inference_ms:.1f}ms\n")
    print("Top-5:")
    for i, item in enumerate(result.top5, start=1):
        print(f"  {i}. {item.label:<40s} {item.confidence:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
