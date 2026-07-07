from datetime import datetime

from pydantic import BaseModel, Field


class ProductSchema(BaseModel):
    id: int = Field(0, description="Product ID")
    admin_id: int = Field(0, description="Admin ID who registered the product (FK → ADMINS.id)")
    name: str = Field("", description="Product name")
    description: str | None = Field(None, description="Product description")
    required_point: int = Field(0, description="Points required to redeem")
    stock: int = Field(0, description="Available stock")
    created_at: datetime = Field(..., description="Product registration time")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "admin_id": 1,
                "name": "Soccer Jersey",
                "description": "Official team jersey",
                "required_point": 1000,
                "stock": 50,
                "created_at": "2026-01-10T00:00:00Z",
            }
        }
    }


class ProductCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    required_point: int = Field(..., ge=0)
    stock: int = Field(..., ge=0)



