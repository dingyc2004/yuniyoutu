from __future__ import annotations

from copy import deepcopy


def _clamp(value: float, minimum: int = 0, maximum: int = 100) -> int:
    return int(max(minimum, min(maximum, round(value))))


def _weather_score(weather: dict, poi: dict) -> tuple[int, list[str]]:
    weather_text = str(weather.get("weather") or "")
    wind_level = int(weather.get("wind_level") or 0)
    warnings: list[str] = []

    if any(token in weather_text for token in ["暴雨", "雷", "台风", "大风"]):
        warnings.append("当前天气存在明显出钓风险。")
        return 25, warnings

    if poi.get("is_banned"):
        warnings.append("该点位存在禁钓或限钓提示。")

    if any(token in weather_text for token in ["晴", "多云"]) and wind_level <= 3:
        return 90, warnings
    if "雨" in weather_text:
        warnings.append("降雨会降低出钓舒适度。")
        return 45, warnings
    if wind_level >= 5:
        warnings.append("风力偏大，注意抛投和岸线安全。")
        return 40, warnings
    return 65, warnings


def _distance_score(distance_m: int) -> int:
    return _clamp(100 - (distance_m / 120), 10, 100)


def _compliance_score(poi: dict) -> int:
    if poi.get("is_banned"):
        return 0
    return int(poi.get("compliance_score") or 75)


def _build_reasons(poi: dict, weather: dict) -> list[str]:
    reasons = [
        poi.get("reason") or "基于示例数据的推荐结果。",
        f"鱼情分 {poi.get('fish_condition_score', 0)}，设施分 {poi.get('facility_score', 0)}。",
    ]
    if weather.get("weather"):
        reasons.append(f"当前天气为 {weather.get('weather')}，风力 {weather.get('wind_level') or 0} 级。")
    return reasons


def rank_pois(pois: list[dict], weather: dict, request: dict) -> dict:
    target = str(request.get("target") or "").strip()
    top_k = int(request.get("top_k") or 3)
    warnings: list[str] = []
    items: list[dict] = []

    for poi in pois:
        poi_copy = deepcopy(poi)
        fish_score = int(poi_copy.get("fish_condition_score") or poi_copy.get("score") or 70)
        compliance_score = _compliance_score(poi_copy)
        distance_score = _distance_score(int(poi_copy.get("distance_m") or 0))
        weather_score, weather_warnings = _weather_score(weather, poi_copy)
        facility_score = int(poi_copy.get("facility_score") or 60)
        social_score = int(poi_copy.get("social_heat") or 60)
        penalty = 0

        if poi_copy.get("is_banned"):
            penalty += 35
            warnings.append(f"{poi_copy['name']} 存在禁钓提示，请先核对规则。")

        if any(flag in {"safety", "slippery"} for flag in (poi_copy.get("risk_flags") or [])):
            penalty += 10

        if target and any(token in target for token in ["路亚", "翘嘴", "鳜鱼"]):
            poi_text = " ".join((poi_copy.get("tags") or []) + (poi_copy.get("fish") or []))
            if any(token in poi_text for token in ["路亚", "翘嘴", "鳜鱼"]):
                fish_score = min(100, fish_score + 5)

        score = _clamp(
            fish_score * 0.25
            + compliance_score * 0.25
            + distance_score * 0.15
            + weather_score * 0.15
            + facility_score * 0.10
            + social_score * 0.10
            - penalty,
        )

        items.append(
            {
                "rank": 0,
                "poi_id": poi_copy["id"],
                "poi_name": poi_copy["name"],
                "score": score,
                "breakdown": {
                    "fish_condition": fish_score,
                    "compliance": compliance_score,
                    "distance": distance_score,
                    "weather": weather_score,
                    "facility": facility_score,
                    "social": social_score,
                    "penalty": penalty,
                },
                "reasons": _build_reasons(poi_copy, weather),
                "warnings": weather_warnings + (["设施或岸线存在安全风险。"] if "safety" in (poi_copy.get("risk_flags") or []) else []),
                "poi": poi_copy,
            }
        )

    items.sort(key=lambda item: item["score"], reverse=True)
    for index, item in enumerate(items, start=1):
        item["rank"] = index

    top_items = items[:top_k]
    if any(poi.get("is_banned") for poi in pois):
        warnings.append("发现禁钓或限钓点位时，应优先提示风险并降低推荐优先级。")

    return {
        "items": top_items,
        "warnings": list(dict.fromkeys(warnings)),
        "strategy": "规则模型优先排序，AI 仅负责解释。",
        "weather": weather,
    }
