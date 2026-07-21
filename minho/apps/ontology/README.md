# 이미지 분류 (ConvNeXt Nano)

`ontology` 앱에 추가된 이미지 분류 기능. ConvNeXt Nano(ImageNet-1k, 1000종)를
ONNX로 변환해 FastAPI 엔드포인트와 MCP tool로 노출한다. 구현 배경/DoD 검증
기록은 [`_docs/image-classifier-agent.md`](_docs/image-classifier-agent.md)와
[`PROGRESS.md`](PROGRESS.md)를 참고.

## 아키텍처

```
                          ┌─────────────────────────────┐
  timm(pretrained)  ─────▶│ scripts/export_onnx.py       │─────▶ models/convnext_nano.onnx
                          └─────────────────────────────┘              (gitignore, 재생성 가능)
                                                                            │
                                                                            ▼
┌──────────────┐   Depends    ┌───────────────────────────┐  loads   ┌──────────────────────────┐
│ FastAPI       │─────────────▶│ ImageClassifierUseCase     │◀────────│ ONNX Runtime Session      │
│ POST /api/    │   (provider  │  = ImageClassifierInteractor│         │ (CUDA면 GPU, 아니면 CPU   │
│ vision/       │   싱글턴)     │  · 전처리(timm resolve_    │         │  자동 폴백)                │
│ classify      │              │    data_config)            │         └──────────────────────────┘
└──────────────┘              │  · top-5 + uncertain 판정   │
       ▲                       └───────────────────────────┘
       │ HTTP(멀티파트 업로드)                ▲
       │                                      │ 같은 인터페이스
┌──────────────────┐                          │
│ MCP classify_image│──────────────────────────┘
│ (/mcp/classifier) │  httpx로 위 FastAPI 엔드포인트 호출
│ 입력: 로컬경로/URL │  (서비스 분리 유지 — 프로세스는 같이 떠 있어도 통신은 HTTP)
└──────────────────┘
       ▲
       │ tool 호출
┌──────────────────┐
│ EXAONE 오케스트레이터│ (다른 MCP tool들과 같은 방식으로 등록)
└──────────────────┘
```

레이어 구조는 이 저장소의 hexagonal 컨벤션을 그대로 따른다:

- `app/dtos/image_classifier_dto.py` — Command/Result (dataclass)
- `app/ports/input/image_classifier_use_case.py` — 입력 포트(ABC)
- `app/ports/output/image_classifier_model_port.py` — 출력 포트(모델 파일 경로)
- `app/use_cases/image_classifier_interactor.py` — 실제 추론 로직
- `adapter/outbound/resource_adapters/onnx/image_classifier_model_adapter.py` — 로컬 파일 어댑터
- `adapter/inbound/api/v1/image_classifier_router.py` — FastAPI 라우터
- `adapter/inbound/api/schema/image_classifier_schemas.py` — Pydantic 응답 스키마
- `adapter/inbound/mcp/image_classifier_tools.py` — MCP tool
- `dependencies/image_classifier_provider.py` — DI 조립(다른 provider와 달리 싱글턴 캐시)

## 실행 방법

### 0) 최초 1회 — ONNX 모델 생성

`*.onnx`는 gitignore 대상이라 저장소에 없다. 아래로 재생성한다(수십 초 소요, 첫
실행 시 timm이 pretrained 가중치를 huggingface에서 내려받는다).

```bash
cd minho
python apps/ontology/scripts/export_onnx.py
```

### 1) 로컬 서버 기동

```bash
cd minho
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

GPU(onnxruntime-gpu)를 쓰려면 `LD_LIBRARY_PATH`에 pip이 설치한 nvidia 라이브러리
경로가 필요하다 — Docker로 띄우면 `docker_entrypoint.py`가 자동으로 설정해주고,
로컬에서 직접 uvicorn을 띄울 땐 아래처럼 직접 잡아줘야 한다(안 해도 CPU로
정상 동작한다).

```bash
export LD_LIBRARY_PATH=$(python -c "import site,glob,os; print(':'.join(sorted(sum((glob.glob(os.path.join(p,'nvidia','*','lib')) for p in site.getsitepackages()), []))))")
```

### 2) API 호출

```bash
curl -X POST -F "file=@sample.jpg" http://127.0.0.1:8000/api/vision/classify
```

### 3) 단독 스크립트 (FastAPI 없이)

```bash
python apps/ontology/scripts/run_classifier_sample.py <이미지 경로>
python apps/ontology/scripts/classifier_scenario_test.py   # 13가지 시나리오 스모크 테스트
```

## API 스펙

**`POST /api/vision/classify`** — `multipart/form-data`, 필드명 `file`(이미지, 최대 10MB)

응답 (`200`):

```json
{
  "ok": true,
  "label": "tabby, tabby cat",
  "confidence": 0.83,
  "top5": [{"label": "tabby, tabby cat", "confidence": 0.83}, "... 4개 더"],
  "uncertain": false,
  "inference_ms": 4.6,
  "message": "classified"
}
```

- `uncertain`: top-1 confidence가 `CLASSIFIER_CONFIDENCE_THRESHOLD`(기본 `0.5`,
  `.env`로 override) 미만이면 `true`.
- 에러: 이미지가 아닌 파일/빈 파일/손상된 이미지 → `422`, 10MB 초과 → `413`.

## MCP tool 등록 방법

`main.py`에 이미 등록되어 있다 — `/mcp/classifier` 경로로 mount됨
(`_ONTOLOGY_MCP_SERVERS`, 기존 `_SILICON_VALLEY_MCP_SERVERS`와 같은 방식).
별도 조치 없이 앱을 띄우면 자동으로 뜬다. 에이전트(EXAONE 오케스트레이터 등)가
Streamable HTTP MCP 클라이언트로 `http://<host>:8000/mcp/classifier`에 붙으면
`classify_image(image_path_or_url: str)` tool을 쓸 수 있다. 입력은 로컬 파일
경로 또는 `http(s)://` 이미지 URL.

## 알려진 한계점

- **ImageNet-1k 1000종 한정** — 도메인 특화 분류(예: 특정 제품, 특정 인물)에는
  fine-tuning이 필요하다. 사람/음식 세부 종류처럼 ImageNet에 없는 카테고리는
  낮은 confidence로 엉뚱한 근접 클래스가 나올 수 있다(`uncertain=true`로 걸러짐).
- **요청당 latency** — `dependencies/image_classifier_provider.py`가 세션을
  프로세스 생애주기 동안 캐시하지만, 프로세스 재시작 직후 첫 요청은 모델
  로드(+ GPU면 CUDA 컨텍스트 초기화)로 수백ms~1s가 걸린다. 이후 요청은 CPU
  기준 수ms~수백ms.
- **GPU 패스스루는 배포 환경에서 별도 설정 필요** — 자세한 내용은
  [`_docs/image-classifier-deployment.md`](_docs/image-classifier-deployment.md).
  GPU가 없어도 CPU로 정상 동작한다(자동 폴백).
- **MCP 프로토콜 왕복 테스트는 tool 함수 직접 호출로 대체** — 실제 MCP
  inspector/JSON-RPC 클라이언트로 왕복 테스트는 하지 않았다(PROGRESS.md
  Phase 3 참고). main.py 기동 시 세션 매니저 등록으로 마운트 자체는 확인함.
- **`import-linter` 아키텍처 검사 미적용** — `pyproject.toml`의 clean-architecture
  layers contract가 아직 `ontology`를 대상 컨테이너로 포함하지 않아(기존 상태),
  이 기능도 자동 검사 대상은 아니다. 기존 `face_detection`/`face_recognition`
  패턴을 수동으로 그대로 따랐다.
