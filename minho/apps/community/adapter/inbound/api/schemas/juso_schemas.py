from __future__ import annotations

from pydantic import BaseModel


class JusoSchema(BaseModel):
    id: int
    name: str


class JusoResponse(BaseModel):
    id: int
    name: str
    role: str
    responsibilities: list[str]
    greeting: str


class JusoContactSchema(BaseModel):
    first_name: str = ""
    middle_name: str = ""
    last_name: str = ""
    phonetic_first_name: str = ""
    phonetic_middle_name: str = ""
    phonetic_last_name: str = ""
    name_prefix: str = ""
    name_suffix: str = ""
    nickname: str = ""
    file_as: str = ""
    organization_name: str = ""
    organization_title: str = ""
    organization_department: str = ""
    birthday: str = ""
    notes: str = ""
    photo: str = ""
    labels: str = ""
    email_1_label: str = ""
    email_1_value: str = ""
    phone_1_label: str = ""
    phone_1_value: str = ""
    phone_2_label: str = ""
    phone_2_value: str = ""
    address_1_label: str = ""
    address_1_formatted: str = ""
    address_1_street: str = ""
    address_1_city: str = ""
    address_1_po_box: str = ""
    address_1_region: str = ""
    address_1_postal_code: str = ""
    address_1_country: str = ""
    address_1_extended_address: str = ""
    website_1_label: str = ""
    website_1_value: str = ""


class JusoUploadResponse(BaseModel):
    ok: bool
    count: int
    message: str


class JusoContactSuggestion(BaseModel):
    nickname: str
    email: str


class JusoSearchResponse(BaseModel):
    results: list[JusoContactSuggestion]
