import os
from pathlib import Path

from dotenv import load_dotenv

# `backend/apps/.env` (Keymaker와 동일 경로 — DB URL 등 공통 env)
_APPS_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_APPS_ROOT / ".env")
load_dotenv()

# 예: postgresql+psycopg://user:password@localhost:5432/dbname
DATABASE_URL = os.getenv("DATABASE_URL")

# 이미지 분류(/classify) top-1 confidence 임계값. 근거는
# ontology/app/dtos/image_classifier_dto.py의 DEFAULT_CONFIDENCE_THRESHOLD 주석 참고.
CLASSIFIER_CONFIDENCE_THRESHOLD = float(os.getenv("CLASSIFIER_CONFIDENCE_THRESHOLD", "0.5"))

# Gemini 키·모델은 `matrix.app.keymaker` 의 Keymaker 가 단일 관리합니다.
