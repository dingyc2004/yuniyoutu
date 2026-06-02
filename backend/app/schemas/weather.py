from datetime import datetime

from pydantic import BaseModel, Field


class WeatherSnapshot(BaseModel):
    city: str
    adcode: str | None = None
    weather: str
    temperature_c: float
    feels_like_c: float | None = None
    wind_direction: str | None = None
    wind_level: int | None = None
    humidity: int | None = None
    pressure_hpa: float | None = None
    visibility_km: float | None = None
    alerts: list[str] = Field(default_factory=list)
    source: str = "seed"
    updated_at: datetime
    forecast: list[dict] = Field(default_factory=list)


class WeatherResponse(BaseModel):
    data: WeatherSnapshot
