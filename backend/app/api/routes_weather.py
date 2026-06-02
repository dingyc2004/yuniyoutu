from fastapi import APIRouter, Query

from app.schemas.weather import WeatherResponse
from app.services.weather_service import get_current_weather

router = APIRouter()


@router.get("/weather/current", response_model=WeatherResponse)
async def read_current_weather(city: str | None = Query(default=None)) -> dict:
    weather = await get_current_weather(city=city)
    return {"data": weather}


@router.get("/weather", response_model=WeatherResponse, include_in_schema=False)
async def read_weather_compat(city: str | None = Query(default=None)) -> dict:
    return await read_current_weather(city=city)
