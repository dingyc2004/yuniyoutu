"""Tests for report service and location obfuscation."""
from fastapi.testclient import TestClient

from app.main import app
from app.services.report_service import get_profile_summary
from app.services.post_service import _obfuscate_location

client = TestClient(app)


def test_profile_summary_returns_structure():
    summary = get_profile_summary("demo_user")
    assert "total_trips" in summary
    assert "total_catches" in summary
    assert "preference" in summary
    assert "efficiency" in summary
    assert "data_sufficient" in summary


def test_report_generation():
    response = client.post("/api/users/demo_user/reports?period=lifetime")
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["period"] == "lifetime"
    assert "data" in data


def test_profile_summary_endpoint():
    response = client.get("/api/users/demo_user/profile-summary")
    assert response.status_code == 200
    assert "data" in response.json()


def test_location_obfuscation_hidden():
    post = {"latitude": 30.5928, "longitude": 114.3055, "location_visibility": "hidden"}
    result = _obfuscate_location(post)
    assert result["latitude"] is None
    assert result["longitude"] is None
    assert result["location_text"] is None


def test_location_obfuscation_city_only():
    post = {"latitude": 30.5928, "longitude": 114.3055, "location_visibility": "city_only"}
    result = _obfuscate_location(post)
    assert result["latitude"] is None
    assert result["longitude"] is None


def test_location_obfuscation_area_blur():
    post = {"latitude": 30.5928, "longitude": 114.3055, "location_visibility": "area_blur"}
    result = _obfuscate_location(post)
    assert result["latitude"] == 30.59
    assert result["longitude"] == 114.31


def test_location_obfuscation_precise():
    post = {"latitude": 30.5928, "longitude": 114.3055, "location_visibility": "precise"}
    result = _obfuscate_location(post)
    assert result["latitude"] == 30.5928
    assert result["longitude"] == 114.3055
