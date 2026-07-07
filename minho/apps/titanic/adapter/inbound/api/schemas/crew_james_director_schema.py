
from pydantic import BaseModel, Field


class JamesDirectorSchema(BaseModel):
    """승객 CSV 행 / 자기소개 데모 공통 스키마."""

    id: int | None = Field(None, description="데모·자기소개용 식별자 (CSV 업로드 시 생략 가능)")
    passenger_id: str | None = Field(None, description="승객 번호")
    survived: str | None = Field(None, description="생존 여부 (0=사망, 1=생존)")
    pclass: str | None = Field(None, description="티켓 등급 (1=1등석, 2=2등석, 3=3등석)")
    name: str | None = Field(None, description="승객 이름")
    gender: str | None = Field(None, description="성별 (male / female) — CSV의 Sex 컬럼을 정규화")
    age: str | None = Field(None, description="나이")
    sib_sp: str | None = Field(None, description="동승한 형제자매/배우자 수")
    parch: str | None = Field(None, description="동승한 부모/자녀 수")
    ticket: str | None = Field(None, description="티켓 번호")
    fare: str | None = Field(None, description="탑승 요금")
    cabin: str | None = Field(None, description="객실 번호")
    embarked: str | None = Field(None, description="탑승 항구 (C=Cherbourg, Q=Queenstown, S=Southampton)")

    model_config = {
        "json_schema_extra" : {
            "example": {
                "passenger_id": "1",
                "survived": "0",
                "pclass": "3",
                "name": "Braund, Mr. Owen Harris",
                "gender": "male",
                "age": "22",
                "sibsp": "1",
                "parch": "0",
                "ticket": "A/5 21171",
                "fare": "7.25",
                "cabin": "",
                "embarked": "S",
            }
        }
     }


class JamesDirectorRecordsSchema(BaseModel):
    """CSV 업로드 등에서 한 번에 넘기는 승객 행 목록."""

    rows: list[JamesDirectorSchema]


class UploadResultSchema(BaseModel):
    saved: int = Field(..., description="저장된 레코드 수")


# 라우터·유스케이스에서 사용하는 CSV 행 스키마 별칭
TitanicRecordSchema = JamesDirectorSchema