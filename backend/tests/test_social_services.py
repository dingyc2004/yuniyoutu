"""Tests for the social and service demo loops."""

from fastapi.testclient import TestClient

from app.data.json_store import load_collection, save_collection
from app.main import app
from app.services.record_service import delete_record

client = TestClient(app)


def test_social_directory_and_notifications():
    social = client.get("/api/users/demo_user/social")
    notifications = client.get("/api/users/demo_user/notifications")
    assert social.status_code == 200
    assert len(social.json()["data"]) >= 3
    assert notifications.status_code == 200
    assert len(notifications.json()["data"]) >= 1


def test_existing_friend_and_direct_message():
    social = client.get("/api/users/demo_user/social")
    friend = next(item for item in social.json()["data"] if item["id"] == "user_jiangfeng")
    assert friend["following"] is True
    assert friend["friend_status"] == "accepted"

    conversation = client.get("/api/direct-messages/demo_user/user_jiangfeng")
    assert conversation.status_code == 200
    assert len(conversation.json()["data"]) >= 2


def test_events_and_equipment_entries():
    events = client.get("/api/events?status=open")
    equipment = client.get("/api/equipment")
    assert events.status_code == 200
    assert len(events.json()["data"]) >= 1
    assert equipment.status_code == 200
    assert len(equipment.json()["data"]) >= 1


def test_event_registration_checkin_history_and_record():
    original_registrations = load_collection("event_registrations")
    original_events = load_collection("events")
    user_id = "test_event_loop_user"
    record_id = None
    try:
        registered = client.post("/api/events/event_001/register", json={"user_id": user_id})
        assert registered.status_code == 201

        history = client.get(f"/api/users/{user_id}/events")
        assert history.status_code == 200
        assert history.json()["data"][0]["registration"]["status"] == "registered"

        checked_in = client.post("/api/events/event_001/checkin", json={"user_id": user_id})
        assert checked_in.status_code == 200
        assert checked_in.json()["data"]["status"] == "checked_in"

        created = client.post("/api/events/event_001/create-record", json={"user_id": user_id})
        assert created.status_code == 201
        record_id = created.json()["data"]["id"]

        repeated = client.post("/api/events/event_001/create-record", json={"user_id": user_id})
        assert repeated.json()["data"]["id"] == record_id
    finally:
        save_collection("event_registrations", original_registrations)
        save_collection("events", original_events)
        if record_id:
            delete_record(record_id)


def test_learning_progress_and_service_recommendations():
    original_progress = load_collection("learning_progress")
    try:
        progress = client.put("/api/tutorials/t_001/progress", json={
            "user_id": "test_learning_user",
            "status": "completed",
            "practice_notes": "完成测试",
        })
        assert progress.status_code == 200
        assert progress.json()["data"]["status"] == "completed"

        listed = client.get("/api/users/test_learning_user/learning-progress")
        assert listed.status_code == 200
        assert listed.json()["data"][0]["tutorial_id"] == "t_001"

        recommendations = client.get("/api/users/demo_user/service-recommendations")
        assert recommendations.status_code == 200
        assert recommendations.json()["data"]["tutorial"]["item"]
        assert recommendations.json()["data"]["event"]["item"]
        assert recommendations.json()["data"]["equipment"]["item"]
    finally:
        save_collection("learning_progress", original_progress)


def test_demo_order_create_pay_and_cancel():
    original_orders = load_collection("orders")
    try:
        created = client.post("/api/orders", json={
            "user_id": "test_order_user",
            "equipment_id": "equip_001",
            "quantity": 1,
        })
        assert created.status_code == 201
        order_id = created.json()["data"]["id"]
        assert created.json()["data"]["status"] == "pending_payment"

        paid = client.post(f"/api/orders/{order_id}/pay", json={"user_id": "test_order_user"})
        assert paid.status_code == 200
        assert paid.json()["data"]["status"] == "paid_demo"

        cancelled = client.delete(f"/api/orders/{order_id}?user_id=test_order_user")
        assert cancelled.status_code == 200
        assert cancelled.json()["data"]["status"] == "cancelled"
    finally:
        save_collection("orders", original_orders)
