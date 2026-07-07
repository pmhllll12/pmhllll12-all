from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

# (route, english_name, korean_name) — adapter/inbound/api/v1/piper_*_router.py 의 하드코딩 값
CASES = [
    ("hendricks", "Richard Hendricks", "리처드 헨드릭스"),
    ("dunn", "Jared Dunn", "자레드 던"),
    ("gilfoyle", "Bertram Gilfoyle", "버트럼 길포일"),
    ("dinesh", "Dinesh Chugtai", "디네시 추그타이"),
    ("bighetti", "Nelson 'Big Head' Bighetti", "넬슨 '빅헤드' 비게티"),
]


@pytest.mark.parametrize("route, english_name, korean_name", CASES)
def test_myself_introduces_character(
    client: TestClient, route: str, english_name: str, korean_name: str
) -> None:
    response = client.get(f"/api/v1/{route}/myself")

    assert response.status_code == 200
    assert response.json() == {
        "route": route,
        "english_name": english_name,
        "korean_name": korean_name,
    }


def test_root_lists_all_characters(client: TestClient) -> None:
    response = client.get("/api/v1/")

    assert response.status_code == 200
    body = response.json()
    assert len(body["characters"]) == len(CASES)
    assert {c["route"] for c in body["characters"]} == {route for route, _, _ in CASES}
    for route, english_name, korean_name in CASES:
        character = next(c for c in body["characters"] if c["route"] == route)
        assert character["english_name"] == english_name
        assert character["korean_name"] == korean_name
