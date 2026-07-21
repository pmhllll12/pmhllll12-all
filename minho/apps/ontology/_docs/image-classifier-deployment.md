# 이미지 분류(ConvNeXt Nano) 배포 메모

`_docs/image-classifier-agent.md` Phase 4 관련 — 실제 인프라(Cloudflare Tunnel 설정,
배포 파이프라인)를 직접 건드리기 전에 확인이 필요한 항목을 정리한다.

## 1. Cloudflare Tunnel — 새 라우팅 불필요

`/api/vision/classify`와 `/mcp/classifier`는 기존 `minho-backend`(포트 8000) FastAPI
앱에 마운트된 새 경로일 뿐, 별도 서비스/포트가 아니다. `api.pmhllll12.cloud` →
`backend:8000` 으로 가는 기존 Cloudflare Tunnel 라우팅이 그대로 이 경로들도 받는다.
**Tunnel 설정을 새로 추가하거나 바꿀 필요가 없다.**

## 2. GPU 패스스루 — 배포 파이프라인 수정 필요(직접 건드리지 않음)

로컬 검증 결과(PROGRESS.md Phase 1 참고), GPU를 실제로 쓰려면:

1. 컨테이너에 `--gpus all`(또는 compose의 `deploy.resources.reservations.devices`)로
   NVIDIA GPU를 전달해야 한다.
2. 이걸 받으려면 배포 서버(호스트)에 **NVIDIA Container Toolkit**이 설치되어
   Docker 데몬이 `nvidia` 런타임을 알고 있어야 한다 — 이건 서버에 직접 로그인해서
   확인/설치해야 하고, 이 코드 변경만으로는 알 수 없다.
3. `onnxruntime-gpu`가 CUDA를 쓰려면 `LD_LIBRARY_PATH`에 pip이 설치한
   `nvidia-*-cu12` 패키지의 `lib/` 경로들이 들어가야 한다 — 이건
   `docker_entrypoint.py`가 컨테이너 기동 시 자동으로 계산해서 설정하도록
   이미 반영했다(코드만으로 해결됨, 추가 조치 불필요).

**GPU 패스스루가 없어도 서비스는 정상 동작한다** — `onnxruntime`이
`CUDAExecutionProvider` 로드에 실패하면 자동으로 `CPUExecutionProvider`로
폴백한다(`image_classifier_interactor.py`). CPU 추론은 이미지 1장당 대략
20~400ms 수준으로 확인됐다(로컬 개발 PC 기준). 실사용 트래픽이 늘어 GPU가
필요해지면, 위 1~2번을 배포 서버에서 직접 확인한 뒤
`.github/workflows/minho-deploy.yml`의 `docker run`(또는 `docker-compose.yaml`의
`backend` 서비스)에 GPU 전달 옵션을 추가하면 된다 — 이 저장소에서는 그 변경을
하지 않았다(호스트 상태를 확인할 수 없는 상태에서 배포 파이프라인을 바꾸는 건
위험 부담이 커서 사용자 확인 후 진행하는 게 맞다고 판단).

## 3. 컨테이너 안에서 GPU 인식 확인 방법

배포 서버에서 GPU 패스스루를 붙인 뒤, 아래로 확인한다.

```bash
docker exec <container> nvidia-smi
docker logs <container> | grep -i "모델 로드 완료"
```

로그에 `providers=['CUDAExecutionProvider', 'CPUExecutionProvider']`가 찍히면
GPU를 실제로 쓰고 있는 것이고, `providers=['CPUExecutionProvider']`만 있으면
CPU 폴백 상태다.
