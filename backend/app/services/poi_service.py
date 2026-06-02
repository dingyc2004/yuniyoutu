from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from math import asin, cos, radians, sin, sqrt
from typing import Iterable

from app.data.seed_data import SEED_POIS, SEED_TUTORIALS


def _distance_text(distance_m: int) -> str:
    if distance_m >= 1000:
        return f"{distance_m / 1000:.1f}km"
    return f"{distance_m}m"


def _haversine_distance_m(lat1: float, lng1: float, lat2: float, lng2: float) -> int:
    radius = 6371000
    phi1, phi2 = radians(lat1), radians(lat2)
    d_phi = radians(lat2 - lat1)
    d_lambda = radians(lng2 - lng1)
    a = sin(d_phi / 2) ** 2 + cos(phi1) * cos(phi2) * sin(d_lambda / 2) ** 2
    return int(2 * radius * asin(sqrt(a)))


def _clone_poi(poi: dict) -> dict:
    item = deepcopy(poi)
    item["distance_text"] = _distance_text(int(item["distance_m"]))
    item["updated_at"] = item.get("updated_at") or datetime.now(timezone.utc).isoformat()
    return item


def _match_keyword(poi: dict, keyword: str) -> bool:
    if not keyword:
        return True
    keyword_lower = keyword.lower()
    haystack = " ".join(
        [
            str(poi.get("name", "")),
            str(poi.get("type", "")),
            str(poi.get("category", "")),
            str(poi.get("address", "")),
            " ".join(poi.get("tags", [])),
            " ".join(poi.get("fish", [])),
        ]
    ).lower()
    return keyword_lower in haystack


def list_pois(
    *,
    city: str | None = None,
    keyword: str | None = None,
    poi_type: str | None = None,
    lat: float | None = None,
    lng: float | None = None,
    radius_m: int | None = None,
    limit: int | None = None,
) -> list[dict]:
    items = [_clone_poi(poi) for poi in SEED_POIS]

    if city:
        items = [poi for poi in items if poi.get("city") == city or poi.get("city") == "武汉市"]

    if poi_type and poi_type != "全部":
        items = [
            poi
            for poi in items
            if poi.get("type") == poi_type or poi_type in (poi.get("tags") or [])
        ]

    if keyword:
        items = [poi for poi in items if _match_keyword(poi, keyword)]

    if lat is not None and lng is not None:
        for poi in items:
            poi["distance_m"] = _haversine_distance_m(lat, lng, float(poi["lat"]), float(poi["lng"]))
            poi["distance_text"] = _distance_text(int(poi["distance_m"]))
        items.sort(key=lambda poi: poi["distance_m"])
        if radius_m:
            items = [poi for poi in items if int(poi["distance_m"]) <= radius_m]
    else:
        items.sort(key=lambda poi: poi["score"], reverse=True)

    if limit is not None:
        items = items[:limit]

    return items


def get_poi_by_id(poi_id: str) -> dict | None:
    for poi in SEED_POIS:
        if poi["id"] == poi_id:
            return _clone_poi(poi)
    return None


def get_tutorials() -> list[dict]:
    return deepcopy(SEED_TUTORIALS)
