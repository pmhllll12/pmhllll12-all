from fastapi import Depends
from silicon_valley.adapter.outbound.repositories.piper_dinesh_dash_repository import (
    DineshDashRepository,
)
from silicon_valley.app.ports.input.piper_dinesh_dash_use_case import DineshDashUseCase
from silicon_valley.app.ports.output.piper_dinesh_dash_port import DineshDashPort
from silicon_valley.app.use_cases.piper_dinesh_dash_interactor import DineshDashInteractor
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db


def get_dinesh_dash_repository(
    db: AsyncSession = Depends(get_db),
) -> DineshDashPort:
    return DineshDashRepository(session=db)


def get_dinesh_dash_use_case(
    repository: DineshDashPort = Depends(get_dinesh_dash_repository),
) -> DineshDashUseCase:
    return DineshDashInteractor(repository=repository)
