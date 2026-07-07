from fastapi import APIRouter

from community.adapter.inbound.api.v1.community_host_router import community_host_router
from community.adapter.inbound.api.v1.discord_router import discord_router
from community.adapter.inbound.api.v1.email_router import email_router
from community.adapter.inbound.api.v1.juso_router import juso_router
from community.adapter.inbound.api.v1.receiver_router import receiver_router
from community.adapter.inbound.api.v1.telegram_router import telegram_router
from community.adapter.inbound.api.v1.watcher_router import watcher_router

community_router = APIRouter(prefix="/api/community")
community_router.include_router(email_router)
community_router.include_router(community_host_router)
community_router.include_router(juso_router)
community_router.include_router(discord_router)
community_router.include_router(telegram_router)
community_router.include_router(receiver_router)
community_router.include_router(watcher_router)
