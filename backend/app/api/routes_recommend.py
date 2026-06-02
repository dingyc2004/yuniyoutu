from fastapi import APIRouter

from app.schemas.recommendation import RecommendationRequest
from app.services.poi_service import list_pois
from app.services.recommend_service import rank_pois
from app.services.weather_service import get_current_weather

router = APIRouter()


@router.post("/recommendations")
async def create_recommendations(payload: RecommendationRequest) -> dict:
    pois = list_pois(
        city=payload.city,
        keyword=payload.target,
        lat=payload.lat,
        lng=payload.lng,
        radius_m=payload.radius_m,
        limit=20,
    )
    weather = await get_current_weather(city=payload.city)
    ranked = rank_pois(pois, weather, payload.model_dump())
    return {"data": ranked}
