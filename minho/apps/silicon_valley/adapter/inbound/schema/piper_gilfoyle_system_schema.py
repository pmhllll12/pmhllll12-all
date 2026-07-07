from pydantic import BaseModel, Field


class GilfoyleSystemSchema(BaseModel):

    route: str = Field("gilfoyle", description="API route segment")
    english_name: str = Field("Bertram Gilfoyle", description="Character's English name")
    korean_name: str = Field("버트럼 길포일", description="Character's Korean name")
    # 파이드 파이퍼의 시스템 아키텍트. 냉소적이고 까칠하지만 서버 인프라는 누구보다 철저히 지킨다.

    model_config = {
        "json_schema_extra": {
            "example": {
                "route": "gilfoyle",
                "english_name": "Bertram Gilfoyle",
                "korean_name": "버트럼 길포일",
            }
        }
    }
