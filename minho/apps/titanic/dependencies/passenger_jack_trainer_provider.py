from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from titanic.adapter.outbound.repositories.passenger_jack_trainer_repository import (
    JackTrainRepository,
)
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.ports.output.passenger_jack_trainer_port import JackTrainerPort
from titanic.app.use_cases.passenger_jack_trainer_interactor import JackTrainerInteractor

from database import get_db


def get_jack_trainer_repository(
    db: AsyncSession = Depends(get_db),
) -> JackTrainerPort:
    return JackTrainRepository(session=db)


def get_jack_train_use_case(
    repository: JackTrainerPort = Depends(get_jack_trainer_repository),
) -> JackTrainerUseCase:
    return JackTrainerInteractor(repository=repository)



