from __future__ import annotations

import os
from functools import lru_cache

from community.adapter.outbound.kcelectra_content_filter_client import KcElectraContentFilterClient
from community.adapter.outbound.n8n_email_client import N8nEmailClient
from community.adapter.outbound.repositories.juso_contact_repository import JusoContactRepository
from community.app.ports.input.community_host_use_case import CommunityHostUseCase
from community.app.ports.input.discord_use_case import DiscordUseCase
from community.app.ports.input.email_host_use_case import EmailHostUseCase
from community.app.ports.input.juso_use_case import JusoUseCase
from community.app.ports.input.send_email_use_case import SendEmailUseCase
from community.app.ports.input.telegram_use_case import TelegramUseCase
from community.app.ports.output.content_filter_port import ContentFilterPort
from community.app.ports.output.juso_contact_port import JusoContactPort
from community.app.use_cases.community_host_interactor import CommunityHostInteractor
from community.app.use_cases.discord_interactor import DiscordInteractor
from community.app.use_cases.email_host_interactor import EmailHostInteractor
from community.app.use_cases.juso_interactor import JusoInteractor
from community.app.use_cases.send_email_interactor import SendEmailInteractor
from community.app.use_cases.telegram_interactor import TelegramInteractor
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db

_DEFAULT_WEBHOOK = "http://localhost:5678/webhook/community-email"


@lru_cache
def get_content_filter_port() -> ContentFilterPort:
    return KcElectraContentFilterClient()


def get_send_email_use_case() -> SendEmailUseCase:
    url = os.getenv("N8N_COMMUNITY_EMAIL_WEBHOOK_URL", _DEFAULT_WEBHOOK)
    return SendEmailInteractor(client=N8nEmailClient(webhook_url=url))


def get_community_host_use_case() -> CommunityHostUseCase:
    return CommunityHostInteractor()


def get_juso_contact_repository(
    db: AsyncSession = Depends(get_db),
) -> JusoContactPort:
    return JusoContactRepository(session=db)


def get_juso_use_case(
    repository: JusoContactPort = Depends(get_juso_contact_repository),
) -> JusoUseCase:
    return JusoInteractor(repository=repository)


def get_discord_use_case() -> DiscordUseCase:
    return DiscordInteractor()


def get_telegram_use_case() -> TelegramUseCase:
    return TelegramInteractor()


def get_email_host_use_case() -> EmailHostUseCase:
    return EmailHostInteractor()
