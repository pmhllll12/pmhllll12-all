from __future__ import annotations

import csv
from io import StringIO

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from community.adapter.inbound.api.schemas.juso_schemas import (
    JusoContactSchema,
    JusoResponse,
    JusoSchema,
    JusoSearchResponse,
    JusoUploadResponse,
)
from community.app.ports.input.juso_use_case import JusoUseCase
from community.dependencies.providers import get_juso_use_case

juso_router = APIRouter(prefix="/juso", tags=["juso"])

_COLUMN_MAP: dict[str, str] = {
    "first name": "first_name",
    "middle name": "middle_name",
    "last name": "last_name",
    "phonetic first name": "phonetic_first_name",
    "phonetic middle name": "phonetic_middle_name",
    "phonetic last name": "phonetic_last_name",
    "name prefix": "name_prefix",
    "name suffix": "name_suffix",
    "nickname": "nickname",
    "file as": "file_as",
    "organization name": "organization_name",
    "organization title": "organization_title",
    "organization department": "organization_department",
    "birthday": "birthday",
    "notes": "notes",
    "photo": "photo",
    "labels": "labels",
    "e-mail 1 - label": "email_1_label",
    "e-mail 1 - value": "email_1_value",
    "phone 1 - label": "phone_1_label",
    "phone 1 - value": "phone_1_value",
    "phone 2 - label": "phone_2_label",
    "phone 2 - value": "phone_2_value",
    "address 1 - label": "address_1_label",
    "address 1 - formatted": "address_1_formatted",
    "address 1 - street": "address_1_street",
    "address 1 - city": "address_1_city",
    "address 1 - po box": "address_1_po_box",
    "address 1 - region": "address_1_region",
    "address 1 - postal code": "address_1_postal_code",
    "address 1 - country": "address_1_country",
    "address 1 - extended address": "address_1_extended_address",
    "website 1 - label": "website_1_label",
    "website 1 - value": "website_1_value",
}


def _normalize_row(row: dict) -> dict:
    normalized: dict[str, str] = {}
    for raw_key, value in row.items():
        if raw_key is None:
            continue
        mapped = _COLUMN_MAP.get(raw_key.strip().lower())
        if mapped:
            normalized[mapped] = value or ""
    return normalized


def _parse_csv(text: str) -> list[JusoContactSchema]:
    if not text.strip():
        raise HTTPException(status_code=400, detail="빈 CSV 파일입니다.")
    reader = csv.DictReader(StringIO(text))
    if reader.fieldnames is None:
        raise HTTPException(status_code=400, detail="CSV 헤더를 읽을 수 없습니다.")
    return [JusoContactSchema(**_normalize_row(row)) for row in reader]


@juso_router.get("/myself", response_model=JusoResponse)
async def introduce_myself(
    use_case: JusoUseCase = Depends(get_juso_use_case),
) -> JusoResponse:
    return await use_case.introduce_myself(
        JusoSchema(id=2, name="주소록 관리자")
    )


@juso_router.post("/upload", response_model=JusoUploadResponse, summary="Google 연락처 CSV 업로드")
async def upload_contacts(
    file: UploadFile = File(...),
    use_case: JusoUseCase = Depends(get_juso_use_case),
) -> JusoUploadResponse:
    return await use_case.upload_contacts(
        _parse_csv((await file.read()).decode("utf-8", errors="replace"))
    )


@juso_router.get("/search", response_model=JusoSearchResponse, summary="이메일/닉네임 앞글자 검색")
async def search_contacts(
    q: str = "",
    use_case: JusoUseCase = Depends(get_juso_use_case),
) -> JusoSearchResponse:
    return await use_case.search_contacts(q)
