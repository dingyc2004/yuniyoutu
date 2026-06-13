from fastapi import APIRouter, HTTPException, Query

from app.data.json_store import load_collection
from app.services.report_service import generate_report, get_profile_summary, get_report, list_reports

router = APIRouter()


@router.get("/users/{user_id}/service-recommendations")
async def service_recommendations(user_id: str) -> dict:
    records = [item for item in load_collection("records") if item.get("user_id") == user_id]
    tutorials = load_collection("tutorials")
    events = load_collection("events")
    equipment = load_collection("equipment")
    blank_count = sum(1 for item in records if item.get("is_blank_trip"))
    methods = [item.get("fishing_method") for item in records if item.get("fishing_method")]
    preferred_method = max(set(methods), key=methods.count) if methods else "台钓"

    tutorial = next(
        (item for item in tutorials if "调漂" in item.get("title", "")),
        tutorials[0] if tutorials else None,
    ) if blank_count else next(
        (item for item in tutorials if preferred_method in " ".join(item.get("tags", []))),
        tutorials[0] if tutorials else None,
    )
    event = next((item for item in events if item.get("status") == "open"), events[0] if events else None)
    equipment_item = next(
        (item for item in equipment if preferred_method in item.get("description", "")),
        equipment[0] if equipment else None,
    )
    return {
        "data": {
            "tutorial": {
                "item": tutorial,
                "reason": "根据你的空军复盘，优先补足找底与调漂能力。" if blank_count else f"与你常用的{preferred_method}钓法相关。",
            },
            "event": {"item": event, "reason": "同城活动可把线上经验转化为真实钓友关系。"},
            "equipment": {"item": equipment_item, "reason": f"结合你的{preferred_method}偏好与真实使用战绩推荐。"},
        }
    }


@router.get("/users/{user_id}/profile-summary")
async def read_profile_summary(user_id: str) -> dict:
    return {"data": get_profile_summary(user_id)}


@router.get("/users/{user_id}/reports")
async def read_reports(
    user_id: str,
    period: str = Query(default="lifetime", pattern="^(month|year|lifetime)$"),
) -> dict:
    data = list_reports(user_id)
    if period != "lifetime":
        data = [r for r in data if r.get("period") == period]
    return {"data": data, "meta": {"total": len(data)}}


@router.post("/users/{user_id}/reports", status_code=201)
async def create_report(
    user_id: str,
    period: str = Query(default="lifetime", pattern="^(month|year|lifetime)$"),
) -> dict:
    report = generate_report(user_id, period)
    return {"data": report}


@router.get("/reports/{report_id}")
async def read_single_report(report_id: str) -> dict:
    report = get_report(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"data": report}
