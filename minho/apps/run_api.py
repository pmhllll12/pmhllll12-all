"""로컬 API 서버 — `backend/apps` 에서 실행.

  cd backend\\apps
  python run_api.py

또는:

  python main.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import uvicorn

_BACKEND = Path(__file__).resolve().parent.parent
_APPS = _BACKEND / "apps"

for _path in (_APPS, _BACKEND):
    _entry = str(_path)
    if _entry not in sys.path:
        sys.path.insert(0, _entry)

os.chdir(_BACKEND)

from _import_aliases import install_secom_aliases  # noqa: E402

install_secom_aliases()

API_PORT = int(os.getenv("API_PORT", "8000"))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "127.0.0.1").strip() or "127.0.0.1",
        port=API_PORT,
        reload=os.getenv("UVICORN_RELOAD", "0").lower() in ("1", "true", "yes"),
        reload_dirs=[str(_BACKEND), str(_APPS)],
        log_level="info",
    )
