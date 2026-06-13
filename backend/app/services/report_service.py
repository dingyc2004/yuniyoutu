from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.data.json_store import load_collection, save_collection


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _record_in_period(record: dict[str, Any], period: str, now: datetime) -> bool:
    if period == "lifetime":
        return True
    try:
        started_at = datetime.fromisoformat(str(record.get("start_time", "")).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return False
    if period == "year":
        return started_at.year == now.year
    if period == "month":
        return started_at.year == now.year and started_at.month == now.month
    return True


def _compute_profile_summary(user_id: str, period: str = "lifetime") -> dict[str, Any]:
    records = load_collection("records")
    now = _utc_now()
    user_records = [
        r
        for r in records
        if r.get("user_id") == user_id and _record_in_period(r, period, now)
    ]

    total_trips = len(user_records)
    total_catches = sum(r.get("fish_count", 0) or 0 for r in user_records)
    total_weight = sum(r.get("fish_weight", 0) or 0 for r in user_records)
    blank_trips = sum(1 for r in user_records if r.get("is_blank_trip", False))
    blank_rate = round(blank_trips / total_trips, 3) if total_trips > 0 else 0

    total_duration = sum(r.get("duration_seconds", 0) or 0 for r in user_records)
    total_hours = total_duration / 3600 if total_duration > 0 else 0

    catch_per_hour = round(total_catches / total_hours, 1) if total_hours > 0 else 0
    weight_per_hour = round(total_weight / total_hours, 1) if total_hours > 0 else 0

    spots = {}
    for r in user_records:
        spot = r.get("fishing_spot_name") or r.get("location_name", "未知")
        spots[spot] = spots.get(spot, 0) + 1
    top_spots = sorted(spots.items(), key=lambda x: x[1], reverse=True)[:5]

    species_count = {}
    species_weight = {}
    for r in user_records:
        s = r.get("fish_species") or "未知"
        species_count[s] = species_count.get(s, 0) + (r.get("fish_count", 0) or 0)
        species_weight[s] = species_weight.get(s, 0) + (r.get("fish_weight", 0) or 0)
    top_species_by_count = sorted(species_count.items(), key=lambda x: x[1], reverse=True)[:5]

    methods_freq = {}
    methods_efficiency = {}
    for r in user_records:
        m = r.get("fishing_method") or "未知"
        methods_freq[m] = methods_freq.get(m, 0) + 1
        duration_h = (r.get("duration_seconds", 0) or 0) / 3600
        if duration_h > 0:
            catch_rate = (r.get("fish_count", 0) or 0) / duration_h
            if m not in methods_efficiency:
                methods_efficiency[m] = []
            methods_efficiency[m].append(catch_rate)

    most_used_method = sorted(methods_freq.items(), key=lambda x: x[1], reverse=True)[0] if methods_freq else ("暂无", 0)
    most_efficient_method = ("暂无", 0)
    if methods_efficiency:
        avg_eff = {m: sum(rates) / len(rates) for m, rates in methods_efficiency.items()}
        most_efficient_method = sorted(avg_eff.items(), key=lambda x: x[1], reverse=True)[0]

    time_slots = {}
    time_slots_efficiency = {}
    for r in user_records:
        start = r.get("start_time", "")
        if start:
            try:
                h = datetime.fromisoformat(str(start).replace("Z", "+00:00")).hour
                slot = _hour_to_slot(h)
                time_slots[slot] = time_slots.get(slot, 0) + 1
                duration_h = (r.get("duration_seconds", 0) or 0) / 3600
                if duration_h > 0:
                    catch_rate = (r.get("fish_count", 0) or 0) / duration_h
                    if slot not in time_slots_efficiency:
                        time_slots_efficiency[slot] = []
                    time_slots_efficiency[slot].append(catch_rate)
            except (ValueError, TypeError):
                pass

    preferred_slot = sorted(time_slots.items(), key=lambda x: x[1], reverse=True)[0] if time_slots else ("暂无", 0)
    best_time_slot = ("暂无", 0)
    if time_slots_efficiency:
        avg_slot_eff = {s: sum(rates) / len(rates) for s, rates in time_slots_efficiency.items()}
        best_time_slot = sorted(avg_slot_eff.items(), key=lambda x: x[1], reverse=True)[0]

    temp_ranges = {}
    for r in user_records:
        t = r.get("temperature")
        if t is not None:
            tr = f"{int(t // 5 * 5)}-{int(t // 5 * 5) + 5}℃"
            temp_ranges[tr] = temp_ranges.get(tr, 0) + 1
    preferred_temp = sorted(temp_ranges.items(), key=lambda x: x[1], reverse=True)[0] if temp_ranges else ("暂无", 0)

    data_sufficient = total_trips >= 5

    return {
        "total_trips": total_trips,
        "total_catches": total_catches,
        "total_weight": round(total_weight, 1),
        "blank_trips": blank_trips,
        "blank_rate": blank_rate,
        "total_hours": round(total_hours, 1),
        "catch_per_hour": catch_per_hour,
        "weight_per_hour": weight_per_hour,
        "top_spots": [{"name": s[0], "count": s[1]} for s in top_spots],
        "top_species_by_count": [{"name": s[0], "count": s[1]} for s in top_species_by_count],
        "top_species_by_weight": [{"name": s[0], "weight": round(s[1], 1)} for s in sorted(species_weight.items(), key=lambda x: x[1], reverse=True)[:5]],
        "preference": {
            "most_used_method": most_used_method[0],
            "most_used_method_count": most_used_method[1],
            "preferred_time_slot": preferred_slot[0],
            "preferred_time_slot_count": preferred_slot[1],
            "preferred_temp_range": preferred_temp[0],
        },
        "efficiency": {
            "most_efficient_method": most_efficient_method[0],
            "most_efficient_method_rate": round(most_efficient_method[1], 1),
            "best_time_slot": best_time_slot[0],
            "best_time_slot_rate": round(best_time_slot[1], 1),
        },
        "data_sufficient": data_sufficient,
    }


def _hour_to_slot(hour: int) -> str:
    if 5 <= hour < 10:
        return "清晨 05:00-09:00"
    elif 10 <= hour < 14:
        return "上午 10:00-13:00"
    elif 14 <= hour < 18:
        return "午后 14:00-17:00"
    elif 18 <= hour < 22:
        return "傍晚 18:00-21:00"
    else:
        return "夜间 22:00-04:00"


def get_profile_summary(user_id: str) -> dict[str, Any]:
    return _compute_profile_summary(user_id)


def generate_report(user_id: str, period: str = "lifetime") -> dict[str, Any]:
    summary = _compute_profile_summary(user_id, period)
    now = _utc_now()
    period_labels = {
        "month": f"{now.year}年{now.month}月",
        "year": f"{now.year}年",
        "lifetime": "生涯汇总",
    }
    report = {
        "id": f"report_{int(now.timestamp() * 1000)}",
        "user_id": user_id,
        "period": period,
        "period_label": period_labels.get(period, "生涯汇总"),
        "data": summary,
        "created_at": now.isoformat(),
    }

    snapshots = load_collection("report_snapshots")
    snapshots.append(report)
    save_collection("report_snapshots", snapshots)

    return report


def list_reports(user_id: str) -> list[dict[str, Any]]:
    snapshots = load_collection("report_snapshots")
    user_reports = [r for r in snapshots if r.get("user_id") == user_id]
    return sorted(user_reports, key=lambda r: r.get("created_at", ""), reverse=True)


def get_report(report_id: str) -> dict | None:
    snapshots = load_collection("report_snapshots")
    for r in snapshots:
        if r.get("id") == report_id:
            return r
    return None
