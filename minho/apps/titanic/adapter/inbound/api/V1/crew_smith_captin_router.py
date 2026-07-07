import logging

from fastapi import APIRouter, Depends
from titanic.adapter.inbound.api.schemas.crew_smith_captin_schemas import (
    SmithCaptainSchema,
    SmithChatRequest,
    SmithChatResponse,
)
from titanic.app.dtos.crew_smith_captin_dto import SmithCaptainResponse
from titanic.app.ports.input.crew_smith_captin_use_case import SmithCaptainUseCase
from titanic.dependencies.crew_smith_captin_provider import get_smith_captain_use_case

logger = logging.getLogger(__name__)

smith_captain_router = APIRouter(prefix="/smith", tags=["smith"])


@smith_captain_router.post("/chat", response_model=SmithChatResponse)
async def smith_titanic_chat(
    schema: SmithChatRequest,
    smith: SmithCaptainUseCase = Depends(get_smith_captain_use_case),
) -> SmithChatResponse:
    logger.info(f"[smith/chat] message={schema.message}")
    return await smith.chat(schema)


@smith_captain_router.get("/myself")
async def introduce_myself(
    smith: SmithCaptainUseCase = Depends(get_smith_captain_use_case),
) -> SmithCaptainResponse:
    return await smith.introduce_myself(
        SmithCaptainSchema(
            id=7,
            name="스미스 선장 (Captain Edward John Smith)",
        )
    )
