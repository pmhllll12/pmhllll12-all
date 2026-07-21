# models — ONNX로 변환된 추론용 모델

`*.onnx`는 gitignore 대상이라 저장소에 포함되지 않는다. 아래 명령으로 재생성한다.

```bash
python apps/ontology/scripts/export_onnx.py
```

[timm](https://github.com/huggingface/pytorch-image-models)의 `convnext_nano.in12k_ft_in1k`
pretrained 가중치를 불러와 `convnext_nano.onnx`로 변환한다(ImageNet-1k, 1000 classes).

`LocalImageClassifierModelAdapter`가 이 파일(`convnext_nano.onnx`)의 절대 경로를 반환한다.
