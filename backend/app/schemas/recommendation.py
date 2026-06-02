from pydantic import BaseModel, Field

from app.schemas.poi import FishingPOI
from app.schemas.weather import WeatherSnapshot


class RecommendationRequest(BaseModel):
    city: str | None = None
    target: str | None = None
    lat: float | None = None
    lng: float | None = None
    radius_m: int = 8000
    top_k: int = 3


class RecommendationBreakdown(BaseModel):
    fish_condition: int
    compliance: int
    distance: int
    weather: int
    facility: int
    social: int
    penalty: int = 0


class RecommendationItem(BaseModel):
    rank: int
    poi_id: str
    poi_name: str
    score: int
    breakdown: RecommendationBreakdown
    reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    poi: FishingPOI


class RecommendationResponse(BaseModel):
    data: dict


class FishingAdviceRequest(BaseModel):
    user_intent: str | None = None
    weather: WeatherSnapshot | None = None
    recommendation: dict | None = None
    candidate_pois: list[dict] = Field(default_factory=list)
