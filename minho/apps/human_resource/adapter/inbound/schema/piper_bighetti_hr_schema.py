from pydantic import BaseModel, Field


class BighettiHrSchema(BaseModel):

    route: str = Field("bighetti", description="API route segment")
    english_name: str = Field("Nelson 'Big Head' Bighetti", description="Character's English name")
    korean_name: str = Field("넬슨 '빅헤드' 비게티", description="Character's Korean name")
    # 실력보다 운으로 늘 좋은 자리를 차지하는 인물. 이번엔 어쩌다 인사(HR) 업무를 맡았다.

    model_config = {
        "json_schema_extra": {
            "example": {
                "route": "bighetti",
                "english_name": "Nelson 'Big Head' Bighetti",
                "korean_name": "넬슨 '빅헤드' 비게티",
            }
        }
    }
