from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    user_id: str = "demo_user"
    equipment_id: str
    quantity: int = Field(default=1, ge=1, le=99)


class OrderAction(BaseModel):
    user_id: str = "demo_user"
