# yolo_train — 사람 얼굴 인식(분류) 데이터셋

YOLO 분류(classification) 포맷으로, 인물 이름별 폴더 안에 그 사람 얼굴 사진을 넣는다.
바운딩 박스 라벨(.txt)은 필요 없다 — 폴더 구조 자체가 라벨이다.

```
yolo_train/
├── train/
│   ├── <인물 이름>/   # 예: ben_afflek/, madonna/ ...
│   │   └── *.jpg
│   └── ...
└── val/
    └── <인물 이름>/
        └── *.jpg
```

`train/`, `val/` 아래의 폴더 이름이 곧 분류 클래스가 된다. `LocalFaceDatasetAdapter`는 이 디렉터리
자체의 절대경로를 반환하고, ultralytics `YOLO(...).train(data=<이 경로>)`가 `train/val` 하위
폴더 구조를 읽어 클래스를 자동으로 구성한다(별도 `data.yaml` 불필요).
