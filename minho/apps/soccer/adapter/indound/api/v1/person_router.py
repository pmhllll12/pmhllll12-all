from fastapi import APIRouter, Depends
from soccer.adapter.indound.api.schemas.person_schemas import PersonCreateSchema, PersonSchema
from soccer.app.dtos.person_dto import PersonResponse
from soccer.app.ports.input.person_use_case import PersonUseCase
from soccer.dependencies.person_provider import get_person_use_case

person_router = APIRouter(prefix="/persons", tags=["persons"])


@person_router.get("/myself", response_model=PersonResponse)
async def introduce_myself(
    person: PersonUseCase = Depends(get_person_use_case),
) -> PersonResponse:
    return await person.introduce_myself(
        PersonSchema(id=1, name="Soccer Person", person_type="player")
    )


@person_router.post("/", response_model=PersonResponse)
async def create_person(
    body: PersonCreateSchema,
    person: PersonUseCase = Depends(get_person_use_case),
) -> PersonResponse:
    return await person.create(body)
