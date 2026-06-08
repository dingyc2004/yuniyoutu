from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from app.data.json_store import load_collection
from app.schemas.record import FishingRecordCreate, FishingRecordPatch


RECORDS_STORAGE: list[dict[str, Any]] = load_collection("records")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _sort_records(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(items, key=lambda item: str(item.get("created_at", "")), reverse=True)


def list_records(*, user_id: str | None = None, limit: int = 20) -> tuple[list[dict[str, Any]], int]:
    items = deepcopy(RECORDS_STORAGE)
    if user_id:
        items = [item for item in items if item.get("user_id") == user_id]
    total = len(items)
    return _sort_records(items)[:limit], total


def get_record(record_id: str) -> dict[str, Any] | None:
    for record in RECORDS_STORAGE:
        if record.get("id") == record_id:
            return deepcopy(record)
    return None


def create_record(payload: FishingRecordCreate) -> dict[str, Any]:
    timestamp = _utc_now()
    timestamp_iso = timestamp.isoformat()
    record = payload.model_dump(mode="json")
    record.update(
        {
            "id": f"record_{int(timestamp.timestamp() * 1000)}",
            "created_at": timestamp_iso,
            "updated_at": timestamp_iso,
        }
    )
    RECORDS_STORAGE.append(record)
    return deepcopy(record)


def update_record(record_id: str, payload: FishingRecordPatch) -> dict[str, Any] | None:
    updates = payload.model_dump(exclude_unset=True, mode="json")
    for index, record in enumerate(RECORDS_STORAGE):
        if record.get("id") == record_id:
            merged = {**record, **updates, "updated_at": _utc_now().isoformat()}
            RECORDS_STORAGE[index] = merged
            return deepcopy(merged)
    return None


def delete_record(record_id: str) -> bool:
    for index, record in enumerate(RECORDS_STORAGE):
        if record.get("id") == record_id:
            RECORDS_STORAGE.pop(index)
            return True
    return False
