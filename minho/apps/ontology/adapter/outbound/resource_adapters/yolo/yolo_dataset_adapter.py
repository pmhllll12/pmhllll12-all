from __future__ import annotations

from pathlib import Path

from ontology.app.ports.output.yolo_port import YoloDatasetPort

_DEFAULT_DATASET_DIR = Path(__file__).resolve().parents[4] / "resources" / "yolo_train"


class YoloDatasetAdapter(YoloDatasetPort):
    """로컬 디렉터리(`apps/vision/resources/yolo_train`)에서 인물별 얼굴 분류 데이터셋을 읽는다.

    나중에 S3 등 다른 소스로 바꾸더라도 YoloDatasetPort를 구현하는 어댑터만 교체하면 되고,
    YoloInteractor(App 영역)는 변경할 필요가 없다.
    """

    def __init__(self, dataset_dir: Path | str = _DEFAULT_DATASET_DIR) -> None:
        self.dataset_dir = Path(dataset_dir)

    def get_dataset_root_path(self) -> str:
        train_dir = self.dataset_dir / "train"
        val_dir = self.dataset_dir / "val"
        if not train_dir.is_dir() or not val_dir.is_dir():
            raise FileNotFoundError(
                f"train/val 폴더를 찾을 수 없습니다: {train_dir}, {val_dir}"
            )
        return str(self.dataset_dir)
