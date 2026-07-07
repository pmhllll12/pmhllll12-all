from __future__ import annotations

from pathlib import Path

from vision.app.ports.output.face_recognition_model_port import FaceRecognitionModelPort

_DEFAULT_MODEL_PATH = (
    Path(__file__).resolve().parents[4]
    / "resources"
    / "yolo_models"
    / "face_recognition"
    / "best.pt"
)


class LocalFaceRecognitionModelAdapter(FaceRecognitionModelPort):
    """로컬 디렉터리(`apps/vision/resources/yolo_models/face_recognition`)에서
    `yolo_interactor`로 파인튜닝한 얼굴 인식(분류) 가중치를 읽는다.

    나중에 S3 등 다른 소스로 바꾸더라도 FaceRecognitionModelPort를 구현하는 어댑터만
    교체하면 되고, FaceRecognitionInteractor(App 영역)는 변경할 필요가 없다.
    """

    def __init__(self, model_path: Path | str = _DEFAULT_MODEL_PATH) -> None:
        self.model_path = Path(model_path)

    def get_model_path(self) -> str:
        if not self.model_path.is_file():
            raise FileNotFoundError(f"얼굴 인식 모델 파일을 찾을 수 없습니다: {self.model_path}")
        return str(self.model_path)
