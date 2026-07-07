import logging

import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from titanic.adapter.outbound.orm.passenger_jack_trainer_orm import JackTrainerOrm
from titanic.adapter.outbound.orm.passenger_rose_model_orm import RoseModelOrm
from titanic.app.dtos.crew_walter_roaster_dto import WalterRoasterQuery, WalterRoasterResponse
from titanic.app.ports.output.crew_walter_roaster_port import WalterRoasterPort

logger = logging.getLogger(__name__)

def _to_row(j: JackTrainerOrm, b: RoseModelOrm | None, include_survived: bool) -> dict:
    row = {
        "PassengerId": j.passenger_id,
        "Name":        j.name,
        "gender":      j.gender,   # 인터렉터가 소문자 gender 기대
        "Age":         j.age,
        "SibSp":       j.sib_sp,
        "Parch":       j.parch,
        "Pclass":      b.pclass   if b else None,
        "Ticket":      b.ticket   if b else None,
        "Fare":        b.fare     if b else None,
        "Cabin":       b.cabin    if b else None,
        "Embarked":    b.embarked if b else None,
    }
    if include_survived:
        row["Survived"] = j.survived
    return row


class WalterRoasterRepository(WalterRoasterPort):
    """PostgreSQL을 이용한 월터의 승객 명단 관리 저장소."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_train_set(self) -> pd.DataFrame:
        ''' Survived 컬럼이 있는 데이터 전체를 데이터 프레임으로 반환하는 메소드 '''
        stmt = (
            select(JackTrainerOrm, RoseModelOrm)
            .outerjoin(RoseModelOrm, RoseModelOrm.passenger_id == JackTrainerOrm.passenger_id)
            .where(JackTrainerOrm.survived.isnot(None))
        )
        result = await self.session.execute(stmt)
        rows = [_to_row(j, b, include_survived=True) for j, b in result.all()]
        logger.info("[WalterRoasterRepository] get_train_set rows=%d", len(rows))
        return pd.DataFrame(rows)

    async def get_test_set(self) -> pd.DataFrame:
        ''' Survived 컬럼이 없는 데이터 전체를 데이터 프레임으로 반환하는 메소드 '''
        stmt = (
            select(JackTrainerOrm, RoseModelOrm)
            .outerjoin(RoseModelOrm, RoseModelOrm.passenger_id == JackTrainerOrm.passenger_id)
            .where(JackTrainerOrm.survived.is_(None))
        )
        result = await self.session.execute(stmt)
        rows = [_to_row(j, b, include_survived=False) for j, b in result.all()]
        logger.info("[WalterRoasterRepository] get_test_set rows=%d", len(rows))
        return pd.DataFrame(rows)
        

    def introduce_myself(self, query: WalterRoasterQuery) -> WalterRoasterResponse:
        logger.info("[WalterRoasterRepository] introduce_myself id=%s name=%s", query.id, query.name)
        return WalterRoasterResponse(
            id=query.id,
            name=query.name,
            memo=query.memo,
        )
