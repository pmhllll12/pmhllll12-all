#!/usr/bin/env python3
"""ConvNeXt Nano(timm) pretrained 가중치를 ONNX로 변환한다.

실행:
    (minho/.venv 활성화 후, 어디서 실행하든 무관 — 경로는 이 파일 기준 상대경로로 계산)
    python apps/ontology/scripts/export_onnx.py
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import onnx
import timm
import torch

# apps/ontology/app/use_cases/image_classifier_interactor.py 의 _MODEL_TAG 와 반드시 일치해야 한다.
_MODEL_TAG = "convnext_nano.in12k_ft_in1k"

_ONTOLOGY_ROOT = Path(__file__).resolve().parents[1]
_OUTPUT_PATH = _ONTOLOGY_ROOT / "models" / "convnext_nano.onnx"
_OPSET = 17


def export_onnx() -> Path:
    print(f"[export_onnx] timm 모델 로드 중: {_MODEL_TAG} (pretrained=True)")
    model = timm.create_model(_MODEL_TAG, pretrained=True, num_classes=1000)
    model.eval()

    input_size = model.pretrained_cfg["input_size"]  # (3, H, W)
    dummy_input = torch.randn(1, *input_size)

    _OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f"[export_onnx] ONNX로 변환 중 → {_OUTPUT_PATH}")
    started = time.perf_counter()
    torch.onnx.export(
        model,
        dummy_input,
        str(_OUTPUT_PATH),
        input_names=["input"],
        output_names=["logits"],
        dynamic_axes={"input": {0: "batch"}, "logits": {0: "batch"}},
        opset_version=_OPSET,
        # 60MB급 소형 모델이라 단일 파일로 충분 — dynamo=True는 외부 데이터로 분리 저장한다
        dynamo=False,
    )
    elapsed = time.perf_counter() - started
    print(f"[export_onnx] 변환 완료 ({elapsed:.1f}s)")

    print("[export_onnx] onnx.checker로 모델 유효성 검증 중")
    onnx_model = onnx.load(str(_OUTPUT_PATH))
    onnx.checker.check_model(onnx_model)
    print(f"[export_onnx] 검증 통과. 파일 크기: {_OUTPUT_PATH.stat().st_size / 1e6:.1f}MB")

    return _OUTPUT_PATH


if __name__ == "__main__":
    try:
        export_onnx()
    except Exception as exc:  # noqa: BLE001 — 스크립트 실행 실패를 명확한 종료 코드로 알린다
        print(f"[export_onnx] 실패: {exc}", file=sys.stderr)
        sys.exit(1)
