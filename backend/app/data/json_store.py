from __future__ import annotations

import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data"


@lru_cache
def _read_json_file(file_name: str) -> Any:
    file_path = DATA_DIR / file_name
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_collection(collection_name: str) -> list[dict[str, Any]]:
    payload = _read_json_file(f"{collection_name}.json")
    if not isinstance(payload, list):
        raise ValueError(f"Collection {collection_name} must be a JSON array.")
    return deepcopy(payload)


def load_latest_weather(city: str | None = None) -> dict[str, Any]:
    snapshots = load_collection("weather_snapshots")
    if city:
        matched = [
            item
            for item in snapshots
            if item.get("city") == city or item.get("adcode") == city
        ]
        if matched:
            return sorted(matched, key=lambda item: item.get("updated_at", ""), reverse=True)[0]
    return sorted(snapshots, key=lambda item: item.get("updated_at", ""), reverse=True)[0]
