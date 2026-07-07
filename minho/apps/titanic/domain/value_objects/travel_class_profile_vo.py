from __future__ import annotations

from dataclasses import dataclass

from titanic.domain.value_objects.cabin_vo import Cabin
from titanic.domain.value_objects.embarked_vo import Embarked
from titanic.domain.value_objects.fare_vo import Fare
from titanic.domain.value_objects.pclass_vo import PClass


@dataclass(frozen=True)
class TravelClassProfile:
    """Survived와 상관관계가 높은 Pclass·Fare·Cabin·Embarked를 묶은 임베디드 값 타입.

    Pclass-Fare 상관(-0.55) 등 서로 강하게 얽혀 있어 개별 필드보다
    하나의 값 타입(승선 등급 프로필)으로 묶는 것이 도메인 의미에 가깝다.
    """

    pclass: PClass
    fare: Fare
    cabin: Cabin
    embarked: Embarked

    @classmethod
    def from_raw(
        cls,
        pclass_raw: str | None,
        fare_raw: str | None,
        cabin_raw: str | None,
        embarked_raw: str | None,
    ) -> TravelClassProfile:
        return cls(
            pclass=PClass.from_raw(pclass_raw),
            fare=Fare.from_raw(fare_raw),
            cabin=Cabin.from_raw(cabin_raw),
            embarked=Embarked.from_raw(embarked_raw),
        )

    def __str__(self) -> str:
        return f"{self.pclass}등급/{self.fare}/{self.cabin}/{self.embarked}"
