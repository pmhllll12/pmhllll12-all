from pydantic import BaseModel, Field


class DunnCooSchema(BaseModel):

    route: str = Field("dunn", description="API route segment")
    english_name: str = Field("Jared Dunn", description="Character's English name")
    korean_name: str = Field("자레드 던", description="Character's Korean name")
    # 파이드 파이퍼의 COO. 헌신적이고 충성스러운 운영 책임자로 회사를 위해 무엇이든 내어준다.

    model_config = {
        "json_schema_extra": {
            "example": {
                "route": "dunn",
                "english_name": "Jared Dunn",
                "korean_name": "자레드 던",
            }
        }
    }
