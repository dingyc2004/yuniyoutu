from datetime import datetime, timezone

from fastapi import APIRouter, Body, HTTPException

from app.data.json_store import load_collection, save_collection

router = APIRouter()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _make_id(prefix: str) -> str:
    return f"{prefix}_{int(_utc_now().timestamp() * 1000)}"


# ─── Comments ───────────────────────────────────────────────

@router.post("/posts/{post_id}/comments", status_code=201)
async def add_comment(post_id: str, payload: dict = Body(...)) -> dict:
    comments = load_collection("comments")
    comment = {
        "id": _make_id("comment"),
        "post_id": post_id,
        "user_id": payload.get("user_id", "demo_user"),
        "author": payload.get("author", "匿名钓友"),
        "content": payload["content"],
        "created_at": _utc_now().isoformat(),
    }
    comments.append(comment)
    save_collection("comments", comments)

    posts = load_collection("posts")
    for p in posts:
        if p.get("id") == post_id:
            p["comments"] = p.get("comments", 0) + 1
            save_collection("posts", posts)
            break

    return {"data": comment}


@router.get("/posts/{post_id}/comments")
async def list_comments(post_id: str) -> dict:
    comments = load_collection("comments")
    post_comments = [c for c in comments if c.get("post_id") == post_id]
    return {"data": sorted(post_comments, key=lambda c: c.get("created_at", ""), reverse=True)}


# ─── Reactions ──────────────────────────────────────────────

@router.post("/posts/{post_id}/reactions", status_code=201)
async def toggle_reaction(post_id: str, payload: dict = Body(...)) -> dict:
    user_id = payload.get("user_id", "demo_user")
    reaction_type = payload.get("reaction_type", "like")

    reactions = load_collection("reactions")
    existing = None
    for i, r in enumerate(reactions):
        if r.get("post_id") == post_id and r.get("user_id") == user_id and r.get("reaction_type") == reaction_type:
            existing = i
            break

    posts = load_collection("posts")
    if existing is not None:
        reactions.pop(existing)
        save_collection("reactions", reactions)
        for p in posts:
            if p.get("id") == post_id:
                p["likes"] = max(0, p.get("likes", 0) - 1)
                save_collection("posts", posts)
                break
        return {"data": {"active": False, "reaction_type": reaction_type}}
    else:
        reaction = {
            "id": _make_id("reaction"),
            "post_id": post_id,
            "user_id": user_id,
            "reaction_type": reaction_type,
            "created_at": _utc_now().isoformat(),
        }
        reactions.append(reaction)
        save_collection("reactions", reactions)
        for p in posts:
            if p.get("id") == post_id:
                p["likes"] = p.get("likes", 0) + 1
                save_collection("posts", posts)
                break
        return {"data": {"active": True, "reaction_type": reaction_type}}


# ─── Follows ─────────────────────────────────────────────────

@router.post("/users/{user_id}/follow", status_code=201)
async def follow_user(user_id: str, payload: dict = Body(...)) -> dict:
    follower_id = payload.get("follower_id", "demo_user")
    follows = load_collection("follows")

    for f in follows:
        if f.get("follower_id") == follower_id and f.get("following_id") == user_id:
            return {"data": {"following": True}}

    follow = {
        "id": _make_id("follow"),
        "follower_id": follower_id,
        "following_id": user_id,
        "created_at": _utc_now().isoformat(),
    }
    follows.append(follow)
    save_collection("follows", follows)
    return {"data": {"following": True}}


@router.delete("/users/{user_id}/follow")
async def unfollow_user(user_id: str, follower_id: str = "demo_user") -> dict:
    follows = load_collection("follows")
    follows = [f for f in follows if not (f.get("follower_id") == follower_id and f.get("following_id") == user_id)]
    save_collection("follows", follows)
    return {"data": {"following": False}}


@router.get("/users/{user_id}/social")
async def social_directory(user_id: str) -> dict:
    users = [u for u in load_collection("users") if u.get("id") != user_id]
    follows = load_collection("follows")
    friendships = load_collection("friendships")
    for user in users:
        target_id = user.get("id")
        user["following"] = any(
            f.get("follower_id") == user_id and f.get("following_id") == target_id
            for f in follows
        )
        user["friend_status"] = next(
            (
                f.get("status")
                for f in friendships
                if {f.get("requester_id"), f.get("addressee_id")} == {user_id, target_id}
            ),
            "none",
        )
    return {"data": users}


@router.post("/users/{user_id}/friend", status_code=201)
async def add_friend(user_id: str, payload: dict = Body(...)) -> dict:
    requester_id = payload.get("requester_id", "demo_user")
    friendships = load_collection("friendships")
    existing = next(
        (
            f
            for f in friendships
            if {f.get("requester_id"), f.get("addressee_id")} == {requester_id, user_id}
        ),
        None,
    )
    if existing:
        return {"data": existing}
    friendship = {
        "id": _make_id("friend"),
        "requester_id": requester_id,
        "addressee_id": user_id,
        "status": "pending",
        "created_at": _utc_now().isoformat(),
    }
    friendships.append(friendship)
    save_collection("friendships", friendships)
    return {"data": friendship}


@router.get("/direct-messages/{user_id}/{peer_id}")
async def list_direct_messages(user_id: str, peer_id: str) -> dict:
    messages = [
        m
        for m in load_collection("direct_messages")
        if {m.get("sender_id"), m.get("receiver_id")} == {user_id, peer_id}
    ]
    return {"data": sorted(messages, key=lambda m: m.get("created_at", ""))}


@router.post("/direct-messages/{peer_id}", status_code=201)
async def send_direct_message(peer_id: str, payload: dict = Body(...)) -> dict:
    messages = load_collection("direct_messages")
    message = {
        "id": _make_id("dm"),
        "sender_id": payload.get("sender_id", "demo_user"),
        "receiver_id": peer_id,
        "content": payload["content"],
        "created_at": _utc_now().isoformat(),
    }
    messages.append(message)
    save_collection("direct_messages", messages)
    return {"data": message}


@router.get("/users/{user_id}/notifications")
async def list_notifications(user_id: str) -> dict:
    items = [
        n for n in load_collection("notifications")
        if n.get("user_id") == user_id
    ]
    return {"data": sorted(items, key=lambda n: n.get("created_at", ""), reverse=True)}
