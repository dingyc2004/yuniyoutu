from datetime import datetime

from pydantic import BaseModel, Field


class CatchEntry(BaseModel):
    id: str
    caught_at: datetime
    species: str
    weight: float = Field(default=0, ge=0)
    length_cm: float | None = Field(default=None, ge=0)
    note: str | None = None


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
    catch_entries: list[CatchEntry] = Field(default_factory=list)
    fishing_method: str | None = None
    bait: str | None = None
    note: str | None = None
    images: list[str] = Field(default_factory=list)
    is_blank_trip: bool = False
    blank_reason: str | None = None
    max_single_weight: float | None = Field(default=None, ge=0)
    equipment_ids: list[str] = Field(default_factory=list)
    water_type: str | None = None
    record_template: str | None = None
    tide: str | None = None
    wave_level: str | None = None
    boat_name: str | None = None
    captain_name: str | None = None
    trip_cost: float | None = Field(default=None, ge=0)
    privacy_level: str = "private"


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
    catch_entries: list[CatchEntry] | None = None
    fishing_method: str | None = None
    bait: str | None = None
    note: str | None = None
    images: list[str] | None = None
    is_blank_trip: bool | None = None
    blank_reason: str | None = None
    max_single_weight: float | None = Field(default=None, ge=0)
    equipment_ids: list[str] | None = None
    water_type: str | None = None
    record_template: str | None = None
    tide: str | None = None
    wave_level: str | None = None
    boat_name: str | None = None
    captain_name: str | None = None
    trip_cost: float | None = Field(default=None, ge=0)
    privacy_level: str | None = None


class FishingRecord(FishingRecordBase):
    id: str
    created_at: datetime
    updated_at: datetime


class FishingRecordResponse(BaseModel):
    data: FishingRecord


class FishingRecordListResponse(BaseModel):
    data: list[FishingRecord]
    meta: dict = Field(default_factory=dict)
