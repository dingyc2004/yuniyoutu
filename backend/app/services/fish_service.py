from __future__ import annotations

from app.data.json_store import load_collection


def list_fish_species() -> list[dict]:
    return load_collection("fish_species")


def get_fish_species_by_name(name: str) -> dict | None:
    normalized = name.strip()
    for fish in list_fish_species():
        aliases = fish.get("alias") or []
        if fish.get("name") == normalized or normalized in aliases:
            return fish
    return None
