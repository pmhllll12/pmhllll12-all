from fastapi import Depends
from admin.adapter.outbound.repositories.piper_gilfoyle_system_repository import (
    GilfoyleSystemRepository,
)
from admin.app.ports.input.piper_gilfoyle_system_use_case import GilfoyleSystemUseCase
from admin.app.ports.output.piper_gilfoyle_system_port import GilfoyleSystemPort
from admin.app.use_cases.piper_gilfoyle_system_interactor import GilfoyleSystemInteractor
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db


def get_gilfoyle_system_repository(
    db: AsyncSession = Depends(get_db),
) -> GilfoyleSystemPort:
    return GilfoyleSystemRepository(session=db)


def get_gilfoyle_system_use_case(
    repository: GilfoyleSystemPort = Depends(get_gilfoyle_system_repository),
) -> GilfoyleSystemUseCase:
    return GilfoyleSystemInteractor(repository=repository)
