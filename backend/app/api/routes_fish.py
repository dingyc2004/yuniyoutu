from fastapi import APIRouter, HTTPException

from app.services.fish_service import get_fish_species_by_name, list_fish_species

router = APIRouter()


@router.get("/fish-species")
async def read_fish_species() -> dict:
    items = list_fish_species()
    return {"data": items, "meta": {"total": len(items), "source": "json"}}


@router.get("/fish-species/{fish_name}")
async def read_fish_species_detail(fish_name: str) -> dict:
    item = get_fish_species_by_name(fish_name)
    if not item:
        raise HTTPException(status_code=404, detail="Fish species not found")
    return {"data": item}
