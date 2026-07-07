"""앱·uvicorn 로깅 설정."""

from __future__ import annotations

import logging
import sys
from typing import Any

_LOG_FMT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

_APP_LOGGER_NAMES = (
    "main",
    "secom",
    "secom.app",
    "secom.app.bootstrap",
    "secom.app.controllers.user_controller",
    "secom.app.services.user_service",
    "secom.app.repositories.user_repository",
    "titanic",
    "titanic.adapter.inbound.api.V1.james_router",
    "titanic.adapter.inbound.api.V1.walter_router",
    "titanic.adapter.outbound.pg.james_pg_repository",
    "titanic.adapter.outbound.pg.walter_pg_repository",
    "titanic.app.ports.input.walter_use_case",
    "titanic.app.ports.output.walter_repository",
    "titanic.app.use_cases.james_command",
    "titanic.app.use_cases.walter_command",
    "titanic.app.use_cases.crew_walter_roaster_interactor",
)

# 포트 모듈은 얇은 경계만 두고 INFO 로그를 남기지 않음 (필요 시 WARNING 이상만).
_QUIET_TITANIC_PORT_LOGGERS = (
    "titanic.app.ports.input.james_use_case",
    "titanic.app.ports.output.james_repository",
)


def setup_app_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format=_LOG_FMT,
        handlers=[logging.StreamHandler(sys.stderr)],
        force=True,
    )
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    for name in _APP_LOGGER_NAMES:
        log = logging.getLogger(name)
        log.setLevel(logging.INFO)
        log.propagate = True
    for name in _QUIET_TITANIC_PORT_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)
    for sql_name in ("sqlalchemy.engine", "sqlalchemy.pool", "sqlalchemy.orm"):
        logging.getLogger(sql_name).setLevel(logging.WARNING)


def get_uvicorn_log_config() -> dict[str, Any]:
    """uvicorn + 앱 로거가 같은 포맷으로 stderr 에 출력되도록 합니다."""
    loggers: dict[str, Any] = {
        "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    }
    for name in _APP_LOGGER_NAMES:
        loggers[name] = {"level": "INFO"}
    for name in _QUIET_TITANIC_PORT_LOGGERS:
        loggers[name] = {"level": "WARNING"}

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {"format": _LOG_FMT},
            "access": {"format": _LOG_FMT},
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stderr",
            },
            "access": {
                "class": "logging.StreamHandler",
                "formatter": "access",
                "stream": "ext://sys.stderr",
            },
        },
        "loggers": loggers,
        "root": {"handlers": ["default"], "level": "INFO"},
    }
