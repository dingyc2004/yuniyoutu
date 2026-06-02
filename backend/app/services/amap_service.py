from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings


async def fetch_amap_poi_list(
    *,
    keywords: str,
    city: str | None = None,
    location: str | None = None,
    radius_m: int = 8000,
    page_size: int = 10,
) -> list[dict[str, Any]] | None:
    if not settings.amap_web_service_key:
        return None

    base_url = "https://restapi.amap.com"
    params: dict[str, Any] = {
        "key": settings.amap_web_service_key,
        "keywords": keywords,
        "output": "JSON",
        "page_size": page_size,
        "page_num": 1,
    }
    path = "/v5/place/text"
    if location:
        path = "/v5/place/around"
        params["location"] = location
        params["radius"] = radius_m
    elif city:
        params["city"] = city

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"{base_url}{path}", params=params)
        response.raise_for_status()
        payload = response.json()

    items = payload.get("pois", {}).get("poi") or payload.get("pois") or payload.get("data", {}).get("pois") or []
    return items if isinstance(items, list) else None


async def fetch_amap_weather_snapshot(
    *,
    city: str,
) -> dict[str, Any] | None:
    if not settings.amap_web_service_key:
        return None

    base_url = "https://restapi.amap.com"
    params = {
        "key": settings.amap_web_service_key,
        "city": city,
        "extensions": "base",
        "output": "JSON",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(f"{base_url}/v3/weather/weatherInfo", params=params)
        response.raise_for_status()
        payload = response.json()

    live = payload.get("lives", [{}])[0] if payload.get("lives") else {}
    if not live:
        return None
    return live
