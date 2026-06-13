from datetime import datetime

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    nickname: str
    avatar: str | None = None
    city: str
    city_code: str | None = None
    level: int = 1
    experience: int = 0
    preferred_methods: list[str] = Field(default_factory=list)
    preferred_species: list[str] = Field(default_factory=list)
    bio: str | None = None


class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime


class UserResponse(BaseModel):
    data: User


class MembershipBase(BaseModel):
    user_id: str
    status: str = "active"
    started_at: datetime | None = None
    expires_at: datetime | None = None


class Membership(MembershipBase):
    id: str
    created_at: datetime
    updated_at: datetime


class MembershipResponse(BaseModel):
    data: Membership
