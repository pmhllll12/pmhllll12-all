from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.adapter.inbound.api.schemas.crew_james_director_schema import JamesDirectorSchema
from titanic.app.dtos.crew_james_director_dto import (
    BookingCommand,
    JamesDirectorQuery,
    JamesDirectorResponse,
    PassengerCommand,
)


class JamesDirectorPort(ABC):
    @abstractmethod
    async def introduce_myself(self, query: JamesDirectorQuery) -> JamesDirectorResponse:
        raise NotImplementedError

    @abstractmethod
    async def upload_titanic_file(self, schema: list[JamesDirectorSchema]) -> JamesDirectorResponse:
        raise NotImplementedError

    @abstractmethod
    async def receive_uploaded_records(
        self,
        person_commands: list[PassengerCommand],
        booking_commands: list[BookingCommand],
    ) -> int:
        raise NotImplementedError
