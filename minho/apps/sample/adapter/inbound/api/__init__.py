from fastapi import APIRouter

from star_craft.adapter.inbound.api.v1.kerrigan_context_router_router import kerrigan_router
from star_craft.adapter.inbound.api.v1.raynor_spoke_registry_router import raynor_router

star_craft_router = APIRouter()
star_craft_router.include_router(kerrigan_router)
star_craft_router.include_router(raynor_router)
