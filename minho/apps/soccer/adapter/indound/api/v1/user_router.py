from fastapi import APIRouter, Depends
from soccer.adapter.indound.api.schemas.user_schemas import UserCreateSchema, UserSchema
from soccer.app.dtos.user_dto import UserResponse
from soccer.app.ports.input.user_use_case import UserUseCase
from soccer.dependencies.user_provider import get_user_use_case

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.get("/myself", response_model=UserResponse)
async def introduce_myself(
    user: UserUseCase = Depends(get_user_use_case),
) -> UserResponse:
    from datetime import datetime
    return await user.introduce_myself(
        UserSchema(
            id=1,
            email="user@example.com",
            nickname="soccer_fan",
            current_point=500,
            created_at=datetime.now(),
        )
    )


@user_router.post("/register", response_model=UserResponse)
async def register(
    body: UserCreateSchema,
    user: UserUseCase = Depends(get_user_use_case),
) -> UserResponse:
    return await user.register(body)
