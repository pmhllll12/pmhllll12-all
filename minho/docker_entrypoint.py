#!/usr/bin/env python3
"""Docker 컨테이너 진입점 — (선택) Alembic 적용 후 uvicorn 으로 FastAPI 기동."""

from __future__ import annotations

import glob
import os
import site
import subprocess
import sys


def _nvidia_ld_library_path() -> str:
    """pip으로 설치된 nvidia-*-cu12 패키지가 번들한 .so 라이브러리 경로들을 모아 반환한다.

    torch는 이 경로들을 스스로 찾아 쓰지만(RPATH), onnxruntime-gpu는 그렇지 않아
    LD_LIBRARY_PATH에 없으면 CUDAExecutionProvider 로드가 조용히 CPU로 폴백한다.
    """
    lib_dirs: list[str] = []
    for site_packages in site.getsitepackages():
        lib_dirs.extend(sorted(glob.glob(os.path.join(site_packages, "nvidia", "*", "lib"))))
    return ":".join(lib_dirs)


def main() -> int:
    os.chdir("/app")
    os.environ.setdefault("API_HOST", "0.0.0.0")
    os.environ.setdefault("UVICORN_RELOAD", "0")

    nvidia_libs = _nvidia_ld_library_path()
    if nvidia_libs:
        existing = os.environ.get("LD_LIBRARY_PATH", "")
        os.environ["LD_LIBRARY_PATH"] = f"{nvidia_libs}:{existing}" if existing else nvidia_libs

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
