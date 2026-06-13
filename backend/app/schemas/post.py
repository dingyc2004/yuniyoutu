from datetime import datetime

from pydantic import BaseModel, Field


class CatchPost(BaseModel):
    id: str
    user_id: str = "demo_user"
    post_type: str
    format: str = "图文"
    author: str
    avatar: str | None = None
    title: str
    content: str
    excerpt: str
    meta: str = ""
    poi_id: str | None = None
    poi_name: str | None = None
    record_id: str | None = None
    content_type: str | None = None
    fish_species: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)
    likes: int = 0
    comments: int = 0
    saves: int = 0
    coverTone: str = "blue"
    visibility: str = "public"
    location_visibility: str = "precise"
    location_text: str | None = None
    location_area_name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    equipment_ids: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class CatchPostCreate(BaseModel):
    user_id: str = "demo_user"
    post_type: str = "鱼获"
    format: str = "图文"
    author: str
    avatar: str | None = None
    title: str
    content: str
    poi_id: str | None = None
    poi_name: str | None = None
    record_id: str | None = None
    content_type: str | None = None
    fish_species: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)
    visibility: str = "public"
    location_visibility: str = "precise"
    location_text: str | None = None
    location_area_name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    equipment_ids: list[str] = Field(default_factory=list)


class CatchPostListResponse(BaseModel):
    data: list[CatchPost]
    meta: dict = Field(default_factory=dict)


class CatchPostResponse(BaseModel):
    data: CatchPost
