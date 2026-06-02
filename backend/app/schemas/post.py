from datetime import datetime

from pydantic import BaseModel, Field


class CatchPost(BaseModel):
    id: str
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
    fish_species: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)
    likes: int = 0
    comments: int = 0
    saves: int = 0
    coverTone: str = "blue"
    visibility: str = "public"
    location_text: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    created_at: datetime
    updated_at: datetime


class CatchPostCreate(BaseModel):
    post_type: str = "鱼获"
    format: str = "图文"
    author: str
    avatar: str | None = None
    title: str
    content: str
    poi_id: str | None = None
    poi_name: str | None = None
    fish_species: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    images: list[str] = Field(default_factory=list)
    visibility: str = "public"
    location_text: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class CatchPostListResponse(BaseModel):
    data: list[CatchPost]
    meta: dict = Field(default_factory=dict)


class CatchPostResponse(BaseModel):
    data: CatchPost
