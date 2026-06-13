from pydantic import BaseModel, Field


class UserAction(BaseModel):
    user_id: str = "demo_user"


class EventCreate(BaseModel):
    title: str = Field(min_length=1)
    organizer_id: str = "demo_user"
    organizer_name: str = ""
    city: str = ""
    water_name: str = ""
    event_time: str | None = None
    duration_hours: int = Field(default=4, ge=1)
    max_participants: int = Field(default=10, ge=1)
    fee: float = Field(default=0, ge=0)
    safety_requirements: str = ""
    description: str = ""
    group_id: str | None = None


class GroupMessageCreate(BaseModel):
    user_id: str = "demo_user"
    author: str = ""
    content: str = Field(min_length=1)
