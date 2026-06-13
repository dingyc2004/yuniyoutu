from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from app.data.json_store import load_collection, save_collection
from app.schemas.post import CatchPostCreate

POSTS_STORAGE: list[dict[str, Any]] = load_collection("posts")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


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


def _persist() -> None:
    save_collection("posts", POSTS_STORAGE)


def _build_post_record(payload: CatchPostCreate) -> dict[str, Any]:
    timestamp = _utc_now()
    timestamp_iso = timestamp.isoformat()
    record = {
        "id": f"post_{int(timestamp.timestamp())}",
        "user_id": payload.user_id,
        "post_type": payload.post_type,
        "format": payload.format,
        "author": payload.author,
        "avatar": payload.avatar or payload.author[:1].upper(),
        "title": payload.title,
        "content": payload.content,
        "excerpt": _build_excerpt(payload.content),
        "meta": payload.poi_name or payload.location_text or payload.location_area_name or "用户发布",
        "poi_id": payload.poi_id,
        "poi_name": payload.poi_name,
        "record_id": payload.record_id,
        "content_type": payload.content_type,
        "fish_species": payload.fish_species,
        "tags": payload.tags,
        "images": payload.images,
        "likes": 0,
        "comments": 0,
        "saves": 0,
        "coverTone": "blue",
        "visibility": payload.visibility,
        "location_visibility": payload.location_visibility,
        "location_text": payload.location_text,
        "location_area_name": payload.location_area_name,
        "latitude": payload.latitude,
        "longitude": payload.longitude,
        "equipment_ids": payload.equipment_ids,
        "created_at": timestamp_iso,
        "updated_at": timestamp_iso,
    }
    return record


def _obfuscate_location(post: dict[str, Any]) -> dict[str, Any]:
    loc_vis = post.get("location_visibility", "precise")
    if loc_vis == "hidden":
        post["latitude"] = None
        post["longitude"] = None
        post["location_text"] = None
    elif loc_vis == "city_only":
        post["latitude"] = None
        post["longitude"] = None
    elif loc_vis == "area_blur":
        if post.get("latitude") is not None and post.get("longitude") is not None:
            post["latitude"] = round(post["latitude"], 2)
            post["longitude"] = round(post["longitude"], 2)
    return post


def list_posts(
    post_type: str | None = None,
    poi_id: str | None = None,
    keyword: str | None = None,
    channel: str | None = None,
    city: str | None = None,
    method: str | None = None,
    species: str | None = None,
    limit: int = 20,
) -> tuple[list[dict[str, Any]], int]:
    items = deepcopy(POSTS_STORAGE)

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
    if channel:
        items = [item for item in items if item.get("content_type") == channel]
    if city and city != "all":
        items = [
            item
            for item in items
            if city in (item.get("location_area_name", "") or "")
        ]
    if method:
        items = [
            item
            for item in items
            if method in " ".join(item.get("tags", []))
        ]
    if species:
        items = [
            item
            for item in items
            if species in (item.get("fish_species", []) or [])
        ]

    total = len(items)
    sorted_items = _sort_posts(items)[:limit]

    public_items = [item for item in sorted_items if item.get("visibility") == "public"]
    obfuscated = [_obfuscate_location(item) for item in public_items]

    return obfuscated, total


def create_post(payload: CatchPostCreate) -> dict[str, Any]:
    record = _build_post_record(payload)
    POSTS_STORAGE.append(record)
    _persist()
    return deepcopy(record)


def get_post(post_id: str) -> dict[str, Any] | None:
    for post in POSTS_STORAGE:
        if post.get("id") == post_id:
            post_copy = deepcopy(post)
            if post_copy.get("visibility") == "public":
                post_copy = _obfuscate_location(post_copy)
            return post_copy
    return None
