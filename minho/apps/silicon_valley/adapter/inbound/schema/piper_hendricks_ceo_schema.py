from pydantic import BaseModel, Field


class HendricksCeoSchema(BaseModel):

    route: str = Field("hendricks", description="API route segment")
    english_name: str = Field("Richard Hendricks", description="Character's English name")
    korean_name: str = Field("리처드 헨드릭스", description="Character's Korean name")
    # 파이드 파이퍼의 창업자 겸 CEO. 압축 알고리즘을 발명해 회사를 세웠지만 사람 다루는 일에는 늘 서툴다.

    model_config = {
        "json_schema_extra": {
            "example": {
                "route": "hendricks",
                "english_name": "Richard Hendricks",
                "korean_name": "리처드 헨드릭스",
            }
        }
    }
