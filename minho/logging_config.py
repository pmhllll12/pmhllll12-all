"""앱·Uvicorn 공통 로깅 — 터미널에서 읽기 쉬운 색·짧은 로거명."""

from __future__ import annotations

import logging
import os
import sys
import time
from typing import Any, Final

# NO_COLOR: https://no-color.org/
_USE_COLOR: Final[bool] = (
    not os.environ.get("NO_COLOR", "").strip()
    and sys.stderr.isatty()
)

_C: dict[str, str] = {
    "RESET": "\033[0m",
    "DIM": "\033[2m",
    "TIME": "\033[90m",
    "DEBUG": "\033[90m",
    "INFO": "\033[32m",
    "WARNING": "\033[33m",
    "ERROR": "\033[31m",
    "CRITICAL": "\033[35m",
    "LOGGER": "\033[36m",
    "HTTP": "\033[35m",
}


def _c(text: str, key: str) -> str:
    if not _USE_COLOR:
        return text
    return f"{_C.get(key, '')}{text}{_C['RESET']}"


def _short_logger(name: str, width: int = 22) -> str:
    """긴 모듈 경로를 짧은 태그로 줄입니다."""
    aliases = {
        "__main__": "app",
        "uvicorn": "uvicorn",
        "uvicorn.error": "uvicorn.err",
        "uvicorn.access": "http",
    }
    if name in aliases:
        short = aliases[name]
    elif name.startswith("titanic.adapter.outbound.pg."):
        short = name.removeprefix("titanic.adapter.outbound.pg.")
    elif name.startswith("titanic."):
        rest = name.removeprefix("titanic.")
        if len(rest) > width:
            short = "…" + rest[-(width - 1) :]
        else:
            short = rest
    else:
        short = name.split(".")[-1] if "." in name else name
    if len(short) > width:
        short = short[: width - 1] + "…"
    return short.ljust(width)


class PrettyFormatter(logging.Formatter):
    """한 줄: 시각 | 레벨 | 짧은로거 | 메시지 (터미널에서만 색)."""

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: str = "%",
        *,
        use_color: bool = True,
    ) -> None:
        # logging.Formatter 는 fmt 가 필요해 더미 문자열 사용 (실제 출력은 format()에서 조립)
        super().__init__(fmt or "%(message)s", datefmt, style)
        self._use_color = bool(use_color) and _USE_COLOR

    def format(self, record: logging.LogRecord) -> str:
        ts = time.strftime("%H:%M:%S", time.localtime(record.created))
        msg = record.getMessage()

        if record.name == "uvicorn.access":
            line = (
                f"{_c(ts, 'TIME') if self._use_color else ts}  "
                f"{_c('HTTP', 'HTTP') if self._use_color else 'HTTP'}  "
                f"{msg}"
            )
            if record.exc_info:
                line += "\n" + self.formatException(record.exc_info)
            return line

        lvl = record.levelname[:4].ljust(4)
        short = _short_logger(record.name)
        if self._use_color:
            lvl_key = record.levelname if record.levelname in _C else "INFO"
            return (
                f"{_c(ts, 'TIME')}  "
                f"{_c(lvl, lvl_key)}  "
                f"{_c(short, 'LOGGER')}  "
                f"{msg}"
            )
        return f"{ts}  {lvl}  {short}  {msg}"


def setup_app_logging(level: int = logging.INFO) -> None:
    """루트에 stderr 핸들러 + PrettyFormatter."""
    root = logging.getLogger()
    root.setLevel(level)

    stderr_streams = (sys.stderr, sys.__stderr__)
    target: logging.StreamHandler | None = None
    for h in root.handlers:
        if isinstance(h, logging.StreamHandler) and getattr(h, "stream", None) in stderr_streams:
            target = h
            break
    if target is None:
        target = logging.StreamHandler(sys.stderr)
        target.setLevel(level)
        root.addHandler(target)
    target.setFormatter(PrettyFormatter())
    target.setLevel(level)

    for name in ("titanic", "adapters", "secom"):
        logging.getLogger(name).setLevel(level)


def get_uvicorn_log_config() -> dict[str, Any]:
    """Uvicorn `log_config` — root·uvicorn 모두 PrettyFormatter."""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "pretty": {
                "()": "logging_config.PrettyFormatter",
                "use_color": True,
            },
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "pretty",
                "stream": "ext://sys.stderr",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
            "uvicorn.error": {"handlers": ["default"], "level": "INFO", "propagate": False},
            "uvicorn.access": {"handlers": ["default"], "level": "INFO", "propagate": False},
        },
        "root": {"level": "INFO", "handlers": ["default"]},
    }
