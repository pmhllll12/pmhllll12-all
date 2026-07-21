# PROGRESS — 이미지 분류 에이전트 (`_docs/image-classifier-agent.md`)

형식: `Phase명 / 상태 / DoD 통과 여부 / 특이사항`

- **Phase 1 — 모델 서빙 레이어** / 완료 / DoD 4개 항목 전부 통과 / `timm.create_model("convnext_nano", pretrained=True)` → `convnext_nano.in12k_ft_in1k` 태그로 자동 해석됨(1000-class, 224x224). `torch.onnx.export`는 `dynamo=True`(기본값)일 때 62MB 가중치를 `.onnx.data`로 분리 저장하길래 `dynamo=False`(레거시 익스포터)로 단일 파일(62.4MB) 생성하도록 변경. `onnxruntime-gpu` 최신(1.27.0)은 CUDA 13을 요구해 설치된 torch(cu126)와 충돌 → `1.24.4`로 다운그레이드해 해결. **중요**: `onnxruntime-gpu`가 CUDA를 실제로 쓰려면 `LD_LIBRARY_PATH`에 `site-packages/nvidia/*/lib` 경로들을 넣어줘야 함(torch는 내부적으로 처리하지만 onnxruntime은 별도) — Phase 4(Docker)에서 반영 필요. GPU 첫 추론은 CUDA 컨텍스트 초기화 때문에 ~1000ms로 CPU(~20ms)보다 느리게 로그되는데, 이는 웜업 비용이라 정상이다(반복 호출 시 수 ms대로 떨어짐 — Phase 2/4에서 세션을 프로세스 생애주기 동안 재사용하므로 실사용에서는 문제 없음).
