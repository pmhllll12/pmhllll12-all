from __future__ import annotations

from abc import ABC, abstractmethod

from community.app.dtos.send_email_dto import SendEmailCommand, SendEmailResult


class SendEmailUseCase(ABC):
    @abstractmethod
    async def send(self, command: SendEmailCommand) -> SendEmailResult:
        raise NotImplementedError
