from fastapi import APIRouter

from app.data.seed_data import SEED_TUTORIALS

router = APIRouter()


@router.get("/tutorials")
async def read_tutorials() -> dict:
    return {"data": SEED_TUTORIALS, "meta": {"total": len(SEED_TUTORIALS), "source": "seed"}}
