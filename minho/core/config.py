import os
from pathlib import Path

from dotenv import load_dotenv

# `backend/apps/.env` (Keymaker와 동일 경로 — DB URL 등 공통 env)
_APPS_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_APPS_ROOT / ".env")
load_dotenv()

# 예: postgresql+psycopg://user:password@localhost:5432/dbname
DATABASE_URL = os.getenv("DATABASE_URL")

# Gemini 키·모델은 `matrix.app.keymaker` 의 Keymaker 가 단일 관리합니다.
