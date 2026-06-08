from fastapi import APIRouter, Body, HTTPException, Query, status

from app.schemas.record import (
    FishingRecordCreate,
    FishingRecordListResponse,
    FishingRecordPatch,
    FishingRecordResponse,
)
from app.services.record_service import create_record, delete_record, get_record, list_records, update_record

router = APIRouter()


@router.get("/records", response_model=FishingRecordListResponse)
async def read_records(
    user_id: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
) -> dict:
    items, total = list_records(user_id=user_id, limit=limit)
    return {"data": items, "meta": {"total": total, "source": "json-memory"}}


@router.post("/records", response_model=FishingRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_fishing_record(payload: FishingRecordCreate = Body(...)) -> dict:
    return {"data": create_record(payload)}


@router.get("/records/{record_id}", response_model=FishingRecordResponse)
async def read_record(record_id: str) -> dict:
    record = get_record(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Fishing record not found")
    return {"data": record}


@router.patch("/records/{record_id}", response_model=FishingRecordResponse)
async def patch_record(record_id: str, payload: FishingRecordPatch = Body(...)) -> dict:
    record = update_record(record_id, payload)
    if not record:
        raise HTTPException(status_code=404, detail="Fishing record not found")
    return {"data": record}


@router.delete("/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_record(record_id: str) -> None:
    if not delete_record(record_id):
        raise HTTPException(status_code=404, detail="Fishing record not found")
