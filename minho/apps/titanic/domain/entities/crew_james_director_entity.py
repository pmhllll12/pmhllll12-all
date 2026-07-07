from __future__ import annotations

from dataclasses import dataclass


@dataclass
class JamesPersonEntity:
    """James 업로드 `PersonOrm` 행과 1:1 대응."""

    passenger_id: str
    name: str
    gender: str
    age: str
    sib_sp: str
    parch: str
    survived: str
    id: int | None = None


@dataclass
class JamesDirectorPersonEntity:
    """`JamesPersonOrm`(titanic_persons) 행과 1:1 대응."""

    passenger_id: str
    booking_id: str
    embarked_code: str
    name: str
    gender: str
    age: str
    sib_sp: str
    parch: str
    survived: str


@dataclass
class JamesDirectorBookingEntity:
    """`JamesBookingOrm`(titanic_bookings) 행과 1:1 대응."""

    booking_id: str
    pclass: str
    ticket: str
    fare: str
    cabin: str
    embarked_code: str
    port_name: str


@dataclass
class JamesBookingEntity:
    """James 업로드 `BookingOrm` 행과 1:1 대응."""

    person_id: int | None
    pclass: str
    ticket: str
    fare: str
    cabin: str
    embarked: str
    id: int | None = None
