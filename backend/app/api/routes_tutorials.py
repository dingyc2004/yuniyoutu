from fastapi import APIRouter

from app.services.poi_service import get_tutorials

router = APIRouter()


@router.get("/tutorials")
async def read_tutorials() -> dict:
    tutorials = get_tutorials()
    return {"data": tutorials, "meta": {"total": len(tutorials), "source": "json"}}
