"""Titanic DIP 의존성 패키지.

`*_schemas`에 대응하던 조립 모듈은 파일명에서 `_schemas`를 빼고 `_provider`로 통일했습니다.

패키지 최상위 `get_*` 이름은 첫 접근 시에만 해당 모듈을 로드합니다.
"""

from __future__ import annotations

import importlib
from typing import Any

_LAZY: dict[str, tuple[str, str]] = {
    "get_andrews_architect_schemas_use_case": (
        "titanic.dependencies.crew_andrews_architect_provider",
        "get_andrews_architect_schemas_use_case",
    ),
    "get_cal_tester_schemas_use_case": (
        "titanic.dependencies.passenger_cal_tester_provider",
        "get_cal_tester_schemas_use_case",
    ),
    "get_crew_andrews_architect_schemas_use_case": (
        "titanic.dependencies.crew_andrews_architect_provider",
        "get_crew_andrews_architect_schemas_use_case",
    ),
    "get_crew_hartley_violin_schemas_use_case": (
        "titanic.dependencies.crew_hartley_violin_provider",
        "get_crew_hartley_violin_schemas_use_case",
    ),
    "get_crew_james_director_use_case": (
        "titanic.dependencies.crew_james_director_provider",
        "get_crew_james_director_use_case",
    ),
    "get_crew_smith_captin_schemas_use_case": (
        "titanic.dependencies.crew_smith_captin_provider",
        "get_crew_smith_captin_schemas_use_case",
    ),
    "get_crew_walter_roaster_use_case": (
        "titanic.dependencies.crew_walter_roaster_provider",
        "get_crew_walter_roaster_use_case",
    ),
    "get_hartley_violin_schemas_use_case": (
        "titanic.dependencies.crew_hartley_violin_provider",
        "get_hartley_violin_schemas_use_case",
    ),
    "get_isidor_couple_schemas_use_case": (
        "titanic.dependencies.passenger_isidor_couple_provider",
        "get_isidor_couple_schemas_use_case",
    ),
    "get_jack_trainer_schemas_use_case": (
        "titanic.dependencies.passenger_jack_trainer_provider",
        "get_jack_trainer_schemas_use_case",
    ),
    "get_james_director_use_case": (
        "titanic.dependencies.crew_james_director_provider",
        "get_james_director_use_case",
    ),
    "get_passenger_cal_tester_schemas_use_case": (
        "titanic.dependencies.passenger_cal_tester_provider",
        "get_passenger_cal_tester_schemas_use_case",
    ),
    "get_passenger_isidor_couple_schemas_use_case": (
        "titanic.dependencies.passenger_isidor_couple_provider",
        "get_passenger_isidor_couple_schemas_use_case",
    ),
    "get_passenger_jack_trainer_schemas_use_case": (
        "titanic.dependencies.passenger_jack_trainer_provider",
        "get_passenger_jack_trainer_schemas_use_case",
    ),
    "get_passenger_rose_model_schemas_use_case": (
        "titanic.dependencies.passenger_rose_model_provider",
        "get_passenger_rose_model_schemas_use_case",
    ),
    "get_passenger_ruth_validation_schemas_use_case": (
        "titanic.dependencies.passenger_ruth_validation_provider",
        "get_passenger_ruth_validation_schemas_use_case",
    ),
    "get_rose_model_schemas_use_case": (
        "titanic.dependencies.passenger_rose_model_provider",
        "get_rose_model_schemas_use_case",
    ),
    "get_ruth_validation_schemas_use_case": (
        "titanic.dependencies.passenger_ruth_validation_provider",
        "get_ruth_validation_schemas_use_case",
    ),
    "get_smith_captin_schemas_use_case": (
        "titanic.dependencies.crew_smith_captin_provider",
        "get_smith_captin_schemas_use_case",
    ),
    "get_walter_roaster_use_case": (
        "titanic.dependencies.crew_walter_roaster_provider",
        "get_walter_roaster_use_case",
    ),
}

__all__ = sorted(_LAZY)


def __getattr__(name: str) -> Any:
    if name not in _LAZY:
        msg = f"module {__name__!r} has no attribute {name!r}"
        raise AttributeError(msg)
    mod_name, attr = _LAZY[name]
    module = importlib.import_module(mod_name)
    value = getattr(module, attr)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted({*(n for n in globals() if not n.startswith("_")), *__all__})
