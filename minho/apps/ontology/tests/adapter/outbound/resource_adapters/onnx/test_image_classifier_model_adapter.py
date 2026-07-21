from __future__ import annotations

from pathlib import Path

import pytest
from ontology.adapter.outbound.resource_adapters.onnx.image_classifier_model_adapter import (
    LocalImageClassifierModelAdapter,
)


def test_get_model_path_raises_when_file_missing(tmp_path: Path):
    adapter = LocalImageClassifierModelAdapter(model_path=tmp_path / "does_not_exist.onnx")
    with pytest.raises(FileNotFoundError):
        adapter.get_model_path()


def test_get_model_path_returns_str_path_when_file_exists(tmp_path: Path):
    model_file = tmp_path / "fake.onnx"
    model_file.write_bytes(b"not a real onnx file, just testing the path plumbing")

    adapter = LocalImageClassifierModelAdapter(model_path=model_file)
    assert adapter.get_model_path() == str(model_file)
