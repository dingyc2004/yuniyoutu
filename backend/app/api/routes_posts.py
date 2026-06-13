from fastapi import APIRouter, Body, Query, status

from app.schemas.post import CatchPostCreate, CatchPostListResponse, CatchPostResponse
from app.services.post_service import create_post, list_posts, get_post

router = APIRouter()


@router.get("/posts", response_model=CatchPostListResponse)
async def read_posts(
    post_type: str | None = None,
    poi_id: str | None = None,
    keyword: str | None = None,
    channel: str | None = None,
    city: str | None = None,
    method: str | None = None,
    species: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
) -> dict:
    items, total = list_posts(
        post_type=post_type,
        poi_id=poi_id,
        keyword=keyword,
        channel=channel,
        city=city,
        method=method,
        species=species,
        limit=limit,
    )
    return {"data": items, "meta": {"total": total, "source": "json"}}


@router.get("/feed", response_model=CatchPostListResponse)
async def read_feed(
    channel: str | None = None,
    city: str | None = None,
    method: str | None = None,
    species: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
) -> dict:
    items, total = list_posts(channel=channel, city=city, method=method, species=species, limit=limit)
    return {"data": items, "meta": {"total": total, "source": "json"}}


@router.post("/posts", response_model=CatchPostResponse, status_code=status.HTTP_201_CREATED)
async def create_new_post(payload: CatchPostCreate = Body(...)) -> dict:
    return {"data": create_post(payload)}


@router.post("/catches", response_model=CatchPostResponse, status_code=status.HTTP_201_CREATED)
async def create_catch(payload: CatchPostCreate = Body(...)) -> dict:
    return {"data": create_post(payload)}


@router.get("/posts/{post_id}", response_model=CatchPostResponse)
async def read_post(post_id: str) -> dict:
    post = get_post(post_id)
    if not post:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Post not found")
    return {"data": post}
