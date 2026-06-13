from fastapi import APIRouter, HTTPException

from app.schemas.user import MembershipResponse, UserResponse
from app.services.user_service import get_user, get_user_membership

router = APIRouter()


@router.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: str) -> dict:
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"data": user}


@router.get("/users/{user_id}/membership", response_model=MembershipResponse)
async def read_user_membership(user_id: str) -> dict:
    membership = get_user_membership(user_id)
    if not membership:
        return {"data": {"id": "", "user_id": user_id, "status": "inactive", "created_at": "", "updated_at": ""}}
    return {"data": membership}
