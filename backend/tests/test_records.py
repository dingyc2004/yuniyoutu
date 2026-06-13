"""Tests for record CRUD and persistence."""
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def test_create_record():
    payload = {
        "user_id": "test_user",
        "start_time": _utc_now_iso(),
        "end_time": _utc_now_iso(),
        "duration_seconds": 7200,
        "location_name": "测试钓点",
        "fish_count": 5,
        "fish_weight": 3.2,
        "fish_species": "鲫鱼",
        "catch_entries": [
            {
                "id": "catch_test_001",
                "caught_at": _utc_now_iso(),
                "species": "鲫鱼",
                "weight": 0.6,
                "length_cm": 24,
                "note": "第一条鱼"
            }
        ],
        "fishing_method": "台钓",
        "bait": "酒米+蚯蚓",
        "note": "测试记录",
        "images": [],
        "is_blank_trip": False,
        "equipment_ids": [],
        "privacy_level": "private",
    }
    response = client.post("/api/records", json=payload)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["fish_species"] == "鲫鱼"
    assert data["fish_count"] == 5
    assert data["fish_weight"] == 3.2
    assert data["fishing_method"] == "台钓"
    assert data["catch_entries"][0]["species"] == "鲫鱼"
    assert data["id"].startswith("record_")


def test_list_records():
    response = client.get("/api/records?user_id=test_user")
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)


def test_get_record_not_found():
    response = client.get("/api/records/nonexistent")
    assert response.status_code == 404


def test_create_blank_trip():
    payload = {
        "user_id": "test_user",
        "start_time": _utc_now_iso(),
        "end_time": _utc_now_iso(),
        "duration_seconds": 3600,
        "location_name": "空军测试点",
        "fish_count": 0,
        "fish_weight": 0.0,
        "fish_species": None,
        "is_blank_trip": True,
        "blank_reason": "水太浑",
        "images": [],
        "equipment_ids": [],
        "privacy_level": "private",
    }
    response = client.post("/api/records", json=payload)
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["is_blank_trip"] is True
    assert data["blank_reason"] == "水太浑"


def test_update_record():
    response = client.post("/api/records", json={
        "user_id": "test_user",
        "start_time": _utc_now_iso(),
        "end_time": _utc_now_iso(),
        "duration_seconds": 1800,
        "location_name": "待更新钓点",
        "fish_count": 1,
        "fish_weight": 0.5,
        "images": [],
        "equipment_ids": [],
        "privacy_level": "private",
    })
    record_id = response.json()["data"]["id"]

    patch_response = client.patch(f"/api/records/{record_id}", json={"note": "更新后的复盘"})
    assert patch_response.status_code == 200
    assert patch_response.json()["data"]["note"] == "更新后的复盘"


def test_delete_record():
    response = client.post("/api/records", json={
        "user_id": "test_user",
        "start_time": _utc_now_iso(),
        "end_time": _utc_now_iso(),
        "duration_seconds": 900,
        "location_name": "待删除",
        "fish_count": 0,
        "fish_weight": 0,
        "images": [],
        "equipment_ids": [],
        "privacy_level": "private",
    })
    record_id = response.json()["data"]["id"]

    del_response = client.delete(f"/api/records/{record_id}")
    assert del_response.status_code == 204

    get_response = client.get(f"/api/records/{record_id}")
    assert get_response.status_code == 404
