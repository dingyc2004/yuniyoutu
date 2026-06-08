from datetime import datetime

from pydantic import BaseModel, Field


class FishingRecordBase(BaseModel):
    user_id: str = "demo_user"
    start_time: datetime
    end_time: datetime
    duration_seconds: int = Field(ge=0)
    fishing_spot_name: str | None = None
    location_name: str
    latitude: float | None = None
    longitude: float | None = None
    weather: str | None = None
    temperature: float | None = None
    fish_count: int = Field(default=0, ge=0)
    fish_weight: float = Field(default=0, ge=0)
    fish_species: str | None = None
    fishing_method: str | None = None
    bait: str | None = None
    note: str | None = None
    images: list[str] = Field(default_factory=list)


class FishingRecordCreate(FishingRecordBase):
    pass


class FishingRecordPatch(BaseModel):
    user_id: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    duration_seconds: int | None = Field(default=None, ge=0)
    fishing_spot_name: str | None = None
    location_name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    weather: str | None = None
    temperature: float | None = None
    fish_count: int | None = Field(default=None, ge=0)
    fish_weight: float | None = Field(default=None, ge=0)
    fish_species: str | None = None
    fishing_method: str | None = None
    bait: str | None = None
    note: str | None = None
    images: list[str] | None = None


class FishingRecord(FishingRecordBase):
    id: str
    created_at: datetime
    updated_at: datetime


class FishingRecordResponse(BaseModel):
    data: FishingRecord


class FishingRecordListResponse(BaseModel):
    data: list[FishingRecord]
    meta: dict = Field(default_factory=dict)
