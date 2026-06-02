from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Body, Query

from app.data.json_store import load_collection
from app.schemas.post import CatchPostCreate, CatchPostListResponse, CatchPostResponse

router = APIRouter()

POSTS_STORAGE: list[dict[str, Any]] = load_collection("posts")


def _sort_posts(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def _sort_key(item: dict[str, Any]) -> str:
        created_at = item.get("created_at", "")
        if isinstance(created_at, datetime):
            return created_at.isoformat()
        return str(created_at)

    return sorted(items, key=_sort_key, reverse=True)


def _build_excerpt(content: str) -> str:
    text = content.strip()
    return text[:48] + ("..." if len(text) > 48 else "")


def _build_post_record(payload: CatchPostCreate) -> dict[str, Any]:
    timestamp = datetime.now(timezone.utc)
    timestamp_iso = timestamp.isoformat()
    record = {
        "id": f"post_{int(timestamp.timestamp())}",
        "post_type": payload.post_type,
        "format": payload.format,
        "author": payload.author,
        "avatar": payload.avatar or payload.author[:1].upper(),
        "title": payload.title,
        "content": payload.content,
        "excerpt": _build_excerpt(payload.content),
        "meta": payload.poi_name or payload.location_text or "用户发布",
        "poi_id": payload.poi_id,
        "poi_name": payload.poi_name,
        "fish_species": payload.fish_species,
        "tags": payload.tags,
        "images": payload.images,
        "likes": 0,
        "comments": 0,
        "saves": 0,
        "coverTone": "blue",
        "visibility": payload.visibility,
        "location_text": payload.location_text,
        "latitude": payload.latitude,
        "longitude": payload.longitude,
        "created_at": timestamp_iso,
        "updated_at": timestamp_iso,
    }
    return record


@router.get("/posts", response_model=CatchPostListResponse)
async def read_posts(
    post_type: str | None = None,
    poi_id: str | None = None,
    keyword: str | None = None,
    limit: int = 20,
) -> dict:
    items = list(POSTS_STORAGE)
    if post_type:
        items = [item for item in items if item.get("post_type") == post_type or item.get("format") == post_type]
    if poi_id:
        items = [item for item in items if item.get("poi_id") == poi_id]
    if keyword:
        keyword_lower = keyword.lower()
        items = [
            item
            for item in items
            if keyword_lower in f"{item.get('title', '')} {item.get('content', '')} {' '.join(item.get('tags', []))}".lower()
        ]
    total = len(items)
    items = _sort_posts(items)[:limit]
    return {"data": items, "meta": {"total": total, "source": "json"}}


@router.get("/feed", response_model=CatchPostListResponse)
async def read_feed(limit: int = 20) -> dict:
    return await read_posts(limit=limit)


@router.post("/posts", response_model=CatchPostResponse, status_code=201)
async def create_post(payload: CatchPostCreate = Body(...)) -> dict:
    record = _build_post_record(payload)
    POSTS_STORAGE.append(record)
    return {"data": record}


@router.post("/catches", response_model=CatchPostResponse, status_code=201)
async def create_catch(payload: CatchPostCreate = Body(...)) -> dict:
    return await create_post(payload)
