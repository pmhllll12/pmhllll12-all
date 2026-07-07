from fastapi import APIRouter, Depends
from soccer.adapter.indound.api.schemas.product_schemas import ProductCreateSchema, ProductSchema
from soccer.app.dtos.product_dto import ProductResponse
from soccer.app.ports.input.product_use_case import ProductUseCase
from soccer.dependencies.product_provider import get_product_use_case

product_router = APIRouter(prefix="/products", tags=["products"])


@product_router.get("/myself", response_model=ProductResponse)
async def introduce_myself(
    product: ProductUseCase = Depends(get_product_use_case),
) -> ProductResponse:
    from datetime import datetime
    return await product.introduce_myself(
        ProductSchema(
            id=1,
            admin_id=1,
            name="Soccer Jersey",
            required_point=1000,
            stock=50,
            created_at=datetime.now(),
        )
    )


@product_router.post("/", response_model=ProductResponse)
async def create_product(
    body: ProductCreateSchema,
    product: ProductUseCase = Depends(get_product_use_case),
) -> ProductResponse:
    return await product.create(body)
