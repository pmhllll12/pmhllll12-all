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

# JWT access token의 aud(audience). 서비스가 하나뿐인 현재는 기본값 "api" 그대로 쓰고,
# 서비스가 늘어나면 배포별로 재정의한다(auth 발급부·백엔드 검증부가 반드시 같은 값을 써야 함).
API_AUD = os.getenv("API_AUD", "api")

# jti 기준 즉시 차단(블랙리스트) Redis 키 접두사. apps.auth(발급부)와
# core.dependencies(검증부) 양쪽이 같은 키를 봐야 해서 여기 하나로 둔다 — core는
# apps.auth를 import할 수 없으므로(auth-isolation 계약) 상수만 공유한다.
AUTHGW_BLACKLIST_PREFIX = "authgw:blacklist:"
