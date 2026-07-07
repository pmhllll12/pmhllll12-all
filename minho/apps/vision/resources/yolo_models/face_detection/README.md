# face_detection — 사전학습 얼굴 탐지 모델

[AdamCodd/YOLOv11n-face-detection](https://huggingface.co/AdamCodd/YOLOv11n-face-detection)
가중치를 사용한다. `*.pt`는 gitignore 대상이라 저장소에 포함되지 않으므로, 최초 1회
아래 명령으로 이 폴더에 받아야 한다.

```bash
curl -L -o model.pt https://huggingface.co/AdamCodd/YOLOv11n-face-detection/resolve/main/model.pt
```

`LocalFaceDetectionModelAdapter`가 이 파일(`model.pt`)의 절대 경로를 반환한다.
