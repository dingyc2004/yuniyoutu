from datetime import datetime, timezone

from fastapi import APIRouter, Body

from app.data.json_store import load_collection, save_collection
from app.schemas.tutorial import LearningProgressUpdate
from app.services.poi_service import get_tutorials

router = APIRouter()


@router.get("/tutorials")
async def read_tutorials() -> dict:
    tutorials = get_tutorials()
    return {"data": tutorials, "meta": {"total": len(tutorials), "source": "json"}}


@router.get("/users/{user_id}/learning-progress")
async def read_learning_progress(user_id: str) -> dict:
    items = [item for item in load_collection("learning_progress") if item.get("user_id") == user_id]
    return {"data": items}


@router.put("/tutorials/{tutorial_id}/progress")
async def update_learning_progress(tutorial_id: str, payload: LearningProgressUpdate = Body(...)) -> dict:
    items = load_collection("learning_progress")
    now = datetime.now(timezone.utc).isoformat()
    existing = next(
        (
            item for item in items
            if item.get("tutorial_id") == tutorial_id and item.get("user_id") == payload.user_id
        ),
        None,
    )
    if existing:
        existing["status"] = payload.status
        existing["practice_notes"] = payload.practice_notes
        existing["updated_at"] = now
        result = existing
    else:
        result = {
            "id": f"progress_{int(datetime.now(timezone.utc).timestamp() * 1000)}",
            "user_id": payload.user_id,
            "tutorial_id": tutorial_id,
            "status": payload.status,
            "practice_notes": payload.practice_notes,
            "created_at": now,
            "updated_at": now,
        }
        items.append(result)
    save_collection("learning_progress", items)
    return {"data": result}
