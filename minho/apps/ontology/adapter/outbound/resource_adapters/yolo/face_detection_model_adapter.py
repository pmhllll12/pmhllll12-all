from __future__ import annotations

from pathlib import Path

from ontology.app.ports.output.face_detection_model_port import FaceDetectionModelPort

_DEFAULT_MODEL_PATH = (
    Path(__file__).resolve().parents[4]
    / "resources"
    / "yolo_models"
    / "face_detection"
    / "model.pt"
)


class LocalFaceDetectionModelAdapter(FaceDetectionModelPort):
    """로컬 디렉터리(`apps/vision/resources/yolo_models/face_detection`)에서 사전학습된
    얼굴 탐지 YOLO 가중치(AdamCodd/YOLOv11n-face-detection)를 읽는다.

    나중에 S3 등 다른 소스로 바꾸더라도 FaceDetectionModelPort를 구현하는 어댑터만
    교체하면 되고, FaceDetectionInteractor(App 영역)는 변경할 필요가 없다.
    """

    def __init__(self, model_path: Path | str = _DEFAULT_MODEL_PATH) -> None:
        self.model_path = Path(model_path)

    def get_model_path(self) -> str:
        if not self.model_path.is_file():
            raise FileNotFoundError(f"얼굴 탐지 모델 파일을 찾을 수 없습니다: {self.model_path}")
        return str(self.model_path)
