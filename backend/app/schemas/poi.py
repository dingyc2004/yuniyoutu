from datetime import datetime

from pydantic import BaseModel, Field


class FishingPOI(BaseModel):
    id: str
    name: str
    type: str
    category: str | None = None
    city: str
    district: str | None = None
    address: str
    location: str
    lng: float
    lat: float
    distance: str
    distance_m: int
    distance_text: str | None = None
    score: int
    fish: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    reason: str
    risk: str
    risk_flags: list[str] = Field(default_factory=list)
    is_banned: bool = False
    facilities: list[str] = Field(default_factory=list)
    social_heat: int = 0
    fish_condition_score: int = 0
    compliance_score: int = 0
    weather_score: int = 0
    facility_score: int = 0
    recent_posts_count: int = 0
    suitability: list[str] = Field(default_factory=list)
    compliance_note: str = ""
    updated_at: datetime


class FishingPOIListResponse(BaseModel):
    data: list[FishingPOI]
    meta: dict = Field(default_factory=dict)


class FishingPOIDetailResponse(BaseModel):
    data: FishingPOI
