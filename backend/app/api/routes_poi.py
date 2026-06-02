from fastapi import APIRouter, HTTPException, Query

from app.schemas.poi import FishingPOIDetailResponse, FishingPOIListResponse
from app.services.poi_service import get_poi_by_id, list_pois

router = APIRouter()


@router.get("/pois", response_model=FishingPOIListResponse)
async def read_pois(
    city: str | None = None,
    keyword: str | None = None,
    poi_type: str | None = Query(default=None, alias="type"),
    lat: float | None = None,
    lng: float | None = None,
    radius_m: int = 8000,
    limit: int = 20,
) -> dict:
    items = list_pois(
        city=city,
        keyword=keyword,
        poi_type=poi_type,
        lat=lat,
        lng=lng,
        radius_m=radius_m,
        limit=None,
    )
    total = len(items)
    return {"data": items[:limit], "meta": {"total": total, "source": "seed"}}


@router.get("/pois/{poi_id}", response_model=FishingPOIDetailResponse)
async def read_poi_detail(poi_id: str) -> dict:
    poi = get_poi_by_id(poi_id)
    if not poi:
        raise HTTPException(status_code=404, detail="POI not found")
    return {"data": poi}
