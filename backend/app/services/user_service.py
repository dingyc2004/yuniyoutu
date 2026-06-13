from __future__ import annotations

from copy import deepcopy

from app.data.json_store import load_collection


def get_user(user_id: str) -> dict | None:
    users = load_collection("users")
    for user in users:
        if user.get("id") == user_id:
            return deepcopy(user)
    return None


def get_user_membership(user_id: str) -> dict | None:
    memberships = load_collection("memberships")
    for m in memberships:
        if m.get("user_id") == user_id:
            return deepcopy(m)
    return None
