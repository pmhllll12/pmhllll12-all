from fastapi import APIRouter, Depends
from soccer.adapter.indound.api.schemas.product_order_schemas import (
    ProductOrderCreateSchema,
    ProductOrderSchema,
)
from soccer.app.dtos.product_order_dto import ProductOrderResponse
from soccer.app.ports.input.product_order_use_case import ProductOrderUseCase
from soccer.dependencies.product_order_provider import get_product_order_use_case

product_order_router = APIRouter(prefix="/orders", tags=["orders"])


@product_order_router.get("/myself", response_model=ProductOrderResponse)
async def introduce_myself(
    order: ProductOrderUseCase = Depends(get_product_order_use_case),
) -> ProductOrderResponse:
    from datetime import datetime
    return await order.introduce_myself(
        ProductOrderSchema(
            id=1,
            user_id=1,
            product_id=1,
            used_point=1000,
            status="pending",
            created_at=datetime.now(),
        )
    )


@product_order_router.post("/", response_model=ProductOrderResponse)
async def create_order(
    body: ProductOrderCreateSchema,
    order: ProductOrderUseCase = Depends(get_product_order_use_case),
) -> ProductOrderResponse:
    return await order.create(body)
