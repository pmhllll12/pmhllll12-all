# face_recognition — 파인튜닝된 얼굴 인식(분류) 모델

`*.pt`는 gitignore 대상이라 저장소에 포함되지 않는다. `resources/yolo_train`의
인물별 데이터셋으로 학습해서 이 폴더에 `best.pt`로 저장해야 한다.

```bash
cd minho
python -c "
from vision.dependencies.face_training_provider import get_face_training_use_case
from vision.app.dtos.face_training_dto import TrainFaceRecognizerCommand
import shutil

result = get_face_training_use_case().train(TrainFaceRecognizerCommand(epochs=30))
shutil.copy(result.weights_path, 'apps/vision/resources/yolo_models/face_recognition/best.pt')
"
```

`LocalFaceRecognitionModelAdapter`가 이 파일(`best.pt`)의 절대 경로를 반환한다.
