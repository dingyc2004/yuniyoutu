from fastapi import APIRouter

from app.schemas.recommendation import FishingAdviceRequest
from app.services.ai_service import generate_fishing_advice

router = APIRouter()


@router.post("/ai/fishing-advice")
async def create_fishing_advice(payload: FishingAdviceRequest) -> dict:
    advice = await generate_fishing_advice(payload.model_dump())
    return {"data": advice}
