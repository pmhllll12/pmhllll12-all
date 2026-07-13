from dataclasses import dataclass


@dataclass(frozen=True) # 생성 후 수정 불가하도록 설정
class BighettiHrQuery:

    route: str
    english_name: str
    korean_name: str


@dataclass(frozen=True) # 생성 후 수정 불가하도록 설정
class BighettiHrResponse:

    route: str
    english_name: str
    korean_name: str
