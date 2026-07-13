from pydantic import BaseModel, Field


class DineshDashSchema(BaseModel):

    route: str = Field("dinesh", description="API route segment")
    english_name: str = Field("Dinesh Chugtai", description="Character's English name")
    korean_name: str = Field("디네시 추그타이", description="Character's Korean name")
    # 파이드 파이퍼의 엔지니어. 길포일과 늘 자존심 대결을 벌이는 코더.

    model_config = {
        "json_schema_extra": {
            "example": {
                "route": "dinesh",
                "english_name": "Dinesh Chugtai",
                "korean_name": "디네시 추그타이",
            }
        }
    }
