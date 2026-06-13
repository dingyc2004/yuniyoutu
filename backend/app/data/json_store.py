from __future__ import annotations

import json
import os
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data"


def _read_json_file(file_name: str) -> Any:
    file_path = DATA_DIR / file_name
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _get_file_path(collection_name: str) -> Path:
    return DATA_DIR / f"{collection_name}.json"


def load_collection(collection_name: str) -> list[dict[str, Any]]:
    payload = _read_json_file(f"{collection_name}.json")
    if not isinstance(payload, list):
        raise ValueError(f"Collection {collection_name} must be a JSON array.")
    return deepcopy(payload)


def save_collection(collection_name: str, items: list[dict[str, Any]]) -> None:
    file_path = _get_file_path(collection_name)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    json_text = json.dumps(items, ensure_ascii=False, indent=2, default=str)

    tmp_fd, tmp_path = tempfile.mkstemp(dir=str(file_path.parent), suffix=".tmp")
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            f.write(json_text)
        os.replace(tmp_path, str(file_path))
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def update_collection(collection_name: str, updater: Callable[[list[dict[str, Any]]], list[dict[str, Any]]]) -> list[dict[str, Any]]:
    items = load_collection(collection_name)
    updated = updater(items)
    save_collection(collection_name, updated)
    return updated


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
