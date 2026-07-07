from fastapi import APIRouter, Depends
from soccer.adapter.indound.api.schemas.admin_schemas import AdminCreateSchema, AdminSchema
from soccer.app.dtos.admin_dto import AdminResponse
from soccer.app.ports.input.admin_use_case import AdminUseCase
from soccer.dependencies.admin_provider import get_admin_use_case

admin_router = APIRouter(prefix="/admins", tags=["admins"])


@admin_router.get("/myself", response_model=AdminResponse)
async def introduce_myself(
    admin: AdminUseCase = Depends(get_admin_use_case),
) -> AdminResponse:
    from datetime import datetime
    return await admin.introduce_myself(
        AdminSchema(
            id=1,
            username="admin01",
            role="super",
            created_at=datetime.now(),
        )
    )


@admin_router.post("/", response_model=AdminResponse)
async def create_admin(
    body: AdminCreateSchema,
    admin: AdminUseCase = Depends(get_admin_use_case),
) -> AdminResponse:
    return await admin.create(body)
