from datetime import datetime, timezone

from datetime import timedelta

from fastapi import APIRouter, Body, HTTPException, Query

from app.data.json_store import load_collection, save_collection
from app.schemas.event import EventCreate, GroupMessageCreate, UserAction
from app.schemas.record import FishingRecordCreate
from app.services.record_service import create_record, get_record

router = APIRouter()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _make_id(prefix: str) -> str:
    return f"{prefix}_{int(_utc_now().timestamp() * 1000)}"


# ─── Events ──────────────────────────────────────────────────

@router.get("/events")
async def list_events(city: str | None = None, status: str | None = None) -> dict:
    events = load_collection("events")
    if city:
        events = [e for e in events if e.get("city") == city]
    if status:
        events = [e for e in events if e.get("status") == status]
    return {"data": sorted(events, key=lambda e: e.get("event_time", ""), reverse=True)}


@router.get("/events/{event_id}")
async def get_event(event_id: str) -> dict:
    events = load_collection("events")
    for e in events:
        if e.get("id") == event_id:
            return {"data": e}
    raise HTTPException(status_code=404, detail="Event not found")


@router.post("/events", status_code=201)
async def create_event(payload: EventCreate = Body(...)) -> dict:
    events = load_collection("events")
    now = _utc_now().isoformat()
    event = {
        "id": _make_id("event"),
        "title": payload.title,
        "organizer_id": payload.organizer_id,
        "organizer_name": payload.organizer_name,
        "city": payload.city,
        "water_name": payload.water_name,
        "event_time": payload.event_time or now,
        "duration_hours": payload.duration_hours,
        "max_participants": payload.max_participants,
        "current_participants": 0,
        "fee": payload.fee,
        "safety_requirements": payload.safety_requirements,
        "description": payload.description,
        "group_id": payload.group_id,
        "status": "open",
        "created_at": now,
        "updated_at": now,
    }
    events.append(event)
    save_collection("events", events)
    return {"data": event}


# ─── Event Registrations ─────────────────────────────────────

@router.post("/events/{event_id}/register", status_code=201)
async def register_event(event_id: str, payload: UserAction = Body(...)) -> dict:
    user_id = payload.user_id

    registrations = load_collection("event_registrations")
    for r in registrations:
        if r.get("event_id") == event_id and r.get("user_id") == user_id:
            if r.get("status") == "cancelled":
                r["status"] = "registered"
                r["checked_in_at"] = None
                save_collection("event_registrations", registrations)
                _change_participant_count(event_id, 1)
                return {"data": r}
            return {"data": {"status": "already_registered"}}

    reg = {
        "id": _make_id("reg"),
        "event_id": event_id,
        "user_id": user_id,
        "status": "registered",
        "checked_in_at": None,
        "created_at": _utc_now().isoformat(),
    }
    registrations.append(reg)
    save_collection("event_registrations", registrations)

    events = load_collection("events")
    for e in events:
        if e.get("id") == event_id:
            e["current_participants"] = e.get("current_participants", 0) + 1
            if e["current_participants"] >= e.get("max_participants", 999):
                e["status"] = "full"
            save_collection("events", events)

            if e.get("group_id"):
                members = load_collection("group_members")
                members.append({
                    "id": _make_id("gm"),
                    "group_id": e["group_id"],
                    "user_id": user_id,
                    "role": "member",
                    "joined_at": _utc_now().isoformat(),
                })
                save_collection("group_members", members)
            break

    return {"data": reg}


def _change_participant_count(event_id: str, delta: int) -> None:
    events = load_collection("events")
    for event in events:
        if event.get("id") == event_id:
            event["current_participants"] = max(0, event.get("current_participants", 0) + delta)
            event["status"] = "full" if event["current_participants"] >= event.get("max_participants", 999) else "open"
            event["updated_at"] = _utc_now().isoformat()
            save_collection("events", events)
            return


@router.delete("/events/{event_id}/register")
async def cancel_registration(event_id: str, user_id: str = "demo_user") -> dict:
    registrations = load_collection("event_registrations")
    for registration in registrations:
        if registration.get("event_id") == event_id and registration.get("user_id") == user_id:
            if registration.get("status") != "cancelled":
                registration["status"] = "cancelled"
                _change_participant_count(event_id, -1)
                save_collection("event_registrations", registrations)
            return {"data": registration}
    raise HTTPException(status_code=404, detail="Registration not found")


@router.get("/users/{user_id}/events")
async def user_event_history(user_id: str) -> dict:
    events_by_id = {event.get("id"): event for event in load_collection("events")}
    items = []
    for registration in load_collection("event_registrations"):
        if registration.get("user_id") != user_id:
            continue
        event = events_by_id.get(registration.get("event_id"))
        if event:
            items.append({**event, "registration": registration})
    return {"data": sorted(items, key=lambda item: item.get("event_time", ""), reverse=True)}


@router.post("/events/{event_id}/checkin")
async def checkin_event(event_id: str, payload: UserAction = Body(...)) -> dict:
    user_id = payload.user_id
    registrations = load_collection("event_registrations")
    for r in registrations:
        if r.get("event_id") == event_id and r.get("user_id") == user_id:
            r["status"] = "checked_in"
            r["checked_in_at"] = _utc_now().isoformat()
            save_collection("event_registrations", registrations)
            return {"data": r}
    raise HTTPException(status_code=404, detail="Registration not found")


@router.post("/events/{event_id}/create-record", status_code=201)
async def create_record_from_event(event_id: str, payload: UserAction = Body(...)) -> dict:
    event = next((item for item in load_collection("events") if item.get("id") == event_id), None)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    registrations = load_collection("event_registrations")
    registration = next(
        (
            item for item in registrations
            if item.get("event_id") == event_id and item.get("user_id") == payload.user_id
        ),
        None,
    )
    if not registration or registration.get("status") != "checked_in":
        raise HTTPException(status_code=409, detail="Check in before creating an event record")
    if registration.get("record_id"):
        existing_record = get_record(registration["record_id"])
        if existing_record:
            return {"data": existing_record}
    start = datetime.fromisoformat(str(event["event_time"]).replace("Z", "+00:00"))
    end = start + timedelta(hours=event.get("duration_hours", 4))
    record = create_record(FishingRecordCreate(
        user_id=payload.user_id,
        start_time=start,
        end_time=end,
        duration_seconds=int((end - start).total_seconds()),
        fishing_spot_name=event.get("water_name") or event.get("title"),
        location_name=event.get("water_name") or event.get("city") or "活动钓点",
        note=f"参与活动：{event.get('title')}。可继续补充鱼获与复盘。",
        images=[],
        privacy_level="private",
    ))
    registration["record_id"] = record["id"]
    save_collection("event_registrations", registrations)
    return {"data": record}


# ─── Groups ──────────────────────────────────────────────────

@router.get("/groups")
async def list_groups(type: str | None = None) -> dict:
    groups = load_collection("groups")
    if type:
        groups = [g for g in groups if g.get("type") == type]
    return {"data": groups}


@router.get("/groups/{group_id}")
async def get_group(group_id: str) -> dict:
    groups = load_collection("groups")
    for g in groups:
        if g.get("id") == group_id:
            return {"data": g}
    raise HTTPException(status_code=404, detail="Group not found")


# ─── Messages ────────────────────────────────────────────────

@router.get("/groups/{group_id}/messages")
async def list_messages(group_id: str, limit: int = Query(default=50, ge=1, le=200)) -> dict:
    messages = load_collection("messages")
    group_msgs = [m for m in messages if m.get("group_id") == group_id]
    sorted_msgs = sorted(group_msgs, key=lambda m: m.get("created_at", ""))
    return {"data": sorted_msgs[-limit:]}


@router.get("/equipment")
async def list_equipment() -> dict:
    return {"data": load_collection("equipment")}


@router.post("/groups/{group_id}/messages", status_code=201)
async def send_message(group_id: str, payload: GroupMessageCreate = Body(...)) -> dict:
    messages = load_collection("messages")
    msg = {
        "id": _make_id("msg"),
        "group_id": group_id,
        "user_id": payload.user_id,
        "author": payload.author,
        "content": payload.content,
        "created_at": _utc_now().isoformat(),
    }
    messages.append(msg)
    save_collection("messages", messages)
    return {"data": msg}
