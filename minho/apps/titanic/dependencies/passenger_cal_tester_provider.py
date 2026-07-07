from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from titanic.adapter.outbound.repositories.passenger_cal_tester_repository import CalTestRepository
from titanic.app.ports.input.passenger_cal_tester_use_case import CalTesterUseCase
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.ports.output.passenger_cal_tester_port import CalTestPort
from titanic.app.use_cases.passenger_cal_tester_interactor import CalTesterInteractor
from titanic.dependencies.passenger_jack_trainer_provider import get_jack_train_use_case

from database import get_db


def get_cal_tester_repository(
    db: AsyncSession = Depends(get_db),
) -> CalTestPort:
    return CalTestRepository(session=db)


def get_cal_test_use_case(
    repository: CalTestPort = Depends(get_cal_tester_repository),
    jack: JackTrainerUseCase = Depends(get_jack_train_use_case),
) -> CalTesterUseCase:
    return CalTesterInteractor(repository=repository, jack=jack)
