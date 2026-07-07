from __future__ import annotations

from titanic.domain.entities.passenger_cal_tester_entity import CalTesterEntity


def cal_tester_default_entity() -> CalTesterEntity:
    return CalTesterEntity()


__all__ = ["cal_tester_default_entity"]
