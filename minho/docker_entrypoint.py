#!/usr/bin/env python3
"""Docker 컨테이너 진입점 — (선택) Alembic 적용 후 uvicorn 으로 FastAPI 기동."""

from __future__ import annotations

import os
import subprocess
import sys


def main() -> int:
    os.chdir("/app")
    os.environ.setdefault("API_HOST", "0.0.0.0")
    os.environ.setdefault("UVICORN_RELOAD", "0")

    if os.getenv("DATABASE_URL", "").strip():
        r = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            check=False,
        )
        if r.returncode != 0:
            print(
                "[docker_entrypoint] alembic upgrade head 실패 (returncode=%s). "
                "DATABASE_URL·마이그레이션을 확인하세요." % r.returncode,
                file=sys.stderr,
            )

    host = os.environ.get("API_HOST", "0.0.0.0").strip() or "0.0.0.0"
    port = str(int(os.environ.get("API_PORT", "8000")))
    return subprocess.call(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            host,
            "--port",
            port,
            "--log-level",
            "info",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
