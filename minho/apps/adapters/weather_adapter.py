"""OpenWeatherMap — 서울 현재 날씨."""

from __future__ import annotations

import os
from typing import Any

import httpx

SEOUL_LAT = 37.5665
SEOUL_LON = 126.9780


def fetch_seoul_weather() -> dict[str, Any]:
    api_key = (os.getenv("OPENWEATHER_API_KEY") or "").strip()
    if not api_key:
        raise ValueError(
            "OPENWEATHER_API_KEY 가 .env 에 없습니다. backend/.env 를 확인하세요."
        )

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": SEOUL_LAT,
        "lon": SEOUL_LON,
        "appid": api_key,
        "units": "metric",
        "lang": "kr",
    }

    with httpx.Client(timeout=10.0) as client:
        response = client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    weather_list = data.get("weather") or [{}]
    w0 = weather_list[0] if weather_list else {}
    main = data.get("main") or {}

    return {
        "city": "Seoul",
        "temp": int(round(float(main.get("temp", 0)))),
        "description": str(w0.get("description", "")),
        "icon": str(w0.get("icon", "01d")),
    }
