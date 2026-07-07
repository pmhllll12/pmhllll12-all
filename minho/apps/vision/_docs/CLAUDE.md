---
type: app
app: vision
---

# vision 앱 — 이미지 분석 (컴퓨터 비전)

이미지를 업로드하면 Gemini 멀티모달로 설명(caption)·태그를 생성해 pgvector(`vision_analyzed_images`)에 저장한다.

---

## 헥사고날 레이어

```
apps/vision/
├── domain/
│   └── analyzed_image.py            # AnalyzedImage 값 객체
├── app/
│   ├── dtos/
│   │   └── vision_dto.py            # AnalyzeImageCommand / Result, AnalyzedImageLog
│   ├── ports/input/
│   │   └── vision_use_case.py       # VisionUseCase (abstract)
│   ├── ports/output/
│   │   ├── vision_port.py           # VisionPort (abstract) — 저장·조회
│   │   └── image_captioning_port.py # ImageCaptioningPort (abstract) — 분석
│   └── use_cases/
│       └── vision_interactor.py     # VisionInteractor
├── adapter/
│   ├── inbound/
│   │   └── api/
│   │       ├── __init__.py               # vision_router 노출
│   │       ├── schemas/vision_schemas.py # AnalyzeImageResponse / AnalyzedImageLogEntry
│   │       └── v1/
│   │           └── vision_router.py      # POST /analyze, GET /logs
│   └── outbound/
│       ├── gemini_vision_client.py       # ImageCaptioningPort 구현 — Gemini 멀티모달
│       ├── orm/vision_orm.py             # SQLAlchemy ORM
│       └── repositories/vision_repository.py  # VisionPort 구현
├── dependencies/
│   └── vision_provider.py           # get_vision_use_case()
└── tests/
    ├── domain/
    │   └── test_analyzed_image.py
    └── app/use_cases/
        └── test_vision_interactor.py
```

**의존성 방향:** `adapter` → `app` → `domain`

---

## API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| `POST` | `/api/vision/analyze` | 이미지 업로드(`multipart/form-data`, `file`) → Gemini 분석 → 저장 |
| `GET` | `/api/vision/logs` | 분석된 이미지 로그 최신순 조회 (최대 100건) |

---

## 환경 변수

| 변수 | 용도 |
|------|------|
| `GEMINI_API_KEY` | Gemini 멀티모달 호출 (`core.matrix.vault_keymaker_secret_manager`) |
| `DATABASE_URL` | pgvector — `vision_analyzed_images` 테이블 |

---

## TDD

```bash
cd minho
python -m pytest apps/vision/tests/ -v
```
