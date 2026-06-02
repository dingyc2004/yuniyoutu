from __future__ import annotations

from datetime import datetime, timezone

from app.core.config import settings
from app.data.json_store import load_latest_weather
from app.services.amap_service import fetch_amap_weather_snapshot


def _to_weather_snapshot(payload: dict, source: str) -> dict:
    return {
        "city": payload.get("city") or settings.default_city_name,
        "adcode": payload.get("adcode"),
        "weather": payload.get("weather") or "未知",
        "temperature_c": float(payload.get("temperature") or payload.get("temperature_c") or 0),
        "feels_like_c": float(payload.get("feels_like") or payload.get("feels_like_c") or payload.get("temperature") or payload.get("temperature_c") or 0),
        "wind_direction": payload.get("winddirection") or payload.get("wind_direction"),
        "wind_level": int(float(payload.get("windpower") or payload.get("wind_level") or 0)),
        "humidity": int(float(payload.get("humidity") or 0)) if payload.get("humidity") is not None else None,
        "pressure_hpa": float(payload.get("pressure_hpa") or payload.get("pressure") or 0) if payload.get("pressure_hpa") or payload.get("pressure") else None,
        "visibility_km": float(payload.get("visibility_km") or payload.get("visibility") or 0) if payload.get("visibility_km") or payload.get("visibility") else None,
        "alerts": payload.get("alerts") or [],
        "source": source,
        "updated_at": datetime.now(timezone.utc),
        "forecast": payload.get("forecast") or [],
    }


async def get_current_weather(*, city: str | None = None) -> dict:
    city_code = city or settings.default_city_code

    if settings.app_env == "production" and settings.amap_web_service_key:
        live = await fetch_amap_weather_snapshot(city=city_code)
        if live:
            return _to_weather_snapshot(live, "amap")

    return _to_weather_snapshot(load_latest_weather(city_code), "seed")
