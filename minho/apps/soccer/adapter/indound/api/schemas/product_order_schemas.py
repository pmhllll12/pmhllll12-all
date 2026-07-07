from datetime import datetime

from pydantic import BaseModel, Field


class ProductOrderSchema(BaseModel):
    id: int = Field(0, description="Order ID")
    user_id: int = Field(0, description="User ID (FK → USERS.id)")
    product_id: int = Field(0, description="Product ID (FK → PRODUCTS.id)")
    used_point: int = Field(0, description="Points used for this order")
    status: str = Field("", description="Order status: pending | confirmed | cancelled")
    created_at: datetime = Field(..., description="Order creation time")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "user_id": 3,
                "product_id": 2,
                "used_point": 1000,
                "status": "pending",
                "created_at": "2026-06-15T10:00:00Z",
            }
        }
    }


class ProductOrderCreateSchema(BaseModel):
    product_id: int


