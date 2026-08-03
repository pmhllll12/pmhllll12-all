"""auth 전용 엔트리포인트 — api(main.py)와 별도 컨테이너로 기동한다.

uvicorn auth_main:app --host 0.0.0.0 --port 9000
"""

import sys
from pathlib import Path

# main.py의 sys.path 구성과 동일하게 맞춘다(core/matrix → 최상위 패키지 이름이
# `matrix`이므로 backend/core를 path에 넣어야 함. check_architecture.sh도 동일).
_BACKEND_ROOT = Path(__file__).resolve().parent
_APPS_ROOT = _BACKEND_ROOT / "apps"
_CORE_ROOT = _BACKEND_ROOT / "core"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))
if str(_APPS_ROOT) not in sys.path:
    sys.path.append(str(_APPS_ROOT))
if str(_CORE_ROOT) not in sys.path:
    sys.path.append(str(_CORE_ROOT))

from auth.router import router as auth_router
from auth.router_mobile import router as auth_mobile_router
from fastapi import FastAPI

app = FastAPI(
    title="RAG Tailor Auth",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
app.include_router(auth_router, prefix="/auth")
# 모바일(Flutter) 경로. 웹과 라우터를 분리해 세션 저장 로직이 섞이지 않게 한다.
app.include_router(auth_mobile_router, prefix="/auth")


@app.get("/healthz")
async def healthz() -> dict[str, bool]:
    return {"ok": True}
