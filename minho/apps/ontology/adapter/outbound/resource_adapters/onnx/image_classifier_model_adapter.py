from __future__ import annotations

from pathlib import Path

from ontology.app.ports.output.image_classifier_model_port import ImageClassifierModelPort

_DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[4] / "models" / "convnext_nano.onnx"


class LocalImageClassifierModelAdapter(ImageClassifierModelPort):
    """로컬 디렉터리(`apps/ontology/models`)에서 `scripts/export_onnx.py`로 변환한
    ConvNeXt Nano ONNX 가중치를 읽는다.

    나중에 S3 등 다른 소스로 바꾸더라도 ImageClassifierModelPort를 구현하는 어댑터만
    교체하면 되고, ImageClassifierInteractor(App 영역)는 변경할 필요가 없다.
    """

    def __init__(self, model_path: Path | str = _DEFAULT_MODEL_PATH) -> None:
        self.model_path = Path(model_path)

    def get_model_path(self) -> str:
        if not self.model_path.is_file():
            raise FileNotFoundError(
                f"이미지 분류 ONNX 모델 파일을 찾을 수 없습니다: {self.model_path} "
                "(scripts/export_onnx.py를 먼저 실행하세요)"
            )
        return str(self.model_path)
