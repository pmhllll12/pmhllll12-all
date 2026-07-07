from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from titanic.adapter.outbound.repositories.crew_smith_captin_repository import (
    SmithCaptainRepository,
)
from titanic.app.ports.input.crew_andrews_architect_use_case import AndrewsArchitectUseCase
from titanic.app.ports.input.crew_hartley_violin_use_case import HartleyViolinUseCase
from titanic.app.ports.input.crew_lowe_boat_use_case import LoweBoatUseCase
from titanic.app.ports.input.crew_smith_captin_use_case import SmithCaptainUseCase
from titanic.app.ports.input.crew_walter_roaster_use_case import WalterRoasterUseCase
from titanic.app.ports.input.passenger_cal_tester_use_case import CalTesterUseCase
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.ports.input.passenger_rose_model_use_case import RoseModelUseCase
from titanic.app.ports.output.crew_smith_captin_port import SmithCaptainPort
from titanic.app.use_cases.crew_smith_captin_interactor import SmithCaptainInteractor
from titanic.dependencies.crew_andrews_architect_provider import get_andrews_architect_use_case
from titanic.dependencies.crew_hartley_violin_provider import get_hartley_violin_use_case
from titanic.dependencies.crew_lowe_boat_provider import get_lowe_boat_use_case
from titanic.dependencies.crew_walter_roaster_provider import get_walter_roaster_use_case
from titanic.dependencies.passenger_cal_tester_provider import get_cal_test_use_case
from titanic.dependencies.passenger_jack_trainer_provider import get_jack_train_use_case
from titanic.dependencies.passenger_rose_model_provider import get_rose_model_use_case

from database import get_db


def get_smith_captain_repository(
    db: AsyncSession = Depends(get_db),
) -> SmithCaptainPort:
    return SmithCaptainRepository(session=db)


def get_smith_captain_use_case(
    repository: SmithCaptainPort          = Depends(get_smith_captain_repository),
    andrews: AndrewsArchitectUseCase      = Depends(get_andrews_architect_use_case),
    jack: JackTrainerUseCase              = Depends(get_jack_train_use_case),
    rose: RoseModelUseCase                = Depends(get_rose_model_use_case),
    cal: CalTesterUseCase                 = Depends(get_cal_test_use_case),
    walter: WalterRoasterUseCase          = Depends(get_walter_roaster_use_case),
    lowe: LoweBoatUseCase                 = Depends(get_lowe_boat_use_case),
    hartley: HartleyViolinUseCase         = Depends(get_hartley_violin_use_case),
) -> SmithCaptainUseCase:
    
    return SmithCaptainInteractor(
        repository=repository,
        jack=jack,
        rose=rose,
        cal=cal,
        walter=walter,
        andrews=andrews,
        lowe=lowe,
        hartley=hartley,
    )
