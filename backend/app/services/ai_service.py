from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings
from app.data.seed_data import SEED_POIS


def _build_mock_advice(candidate_pois: list[dict], recommendation: dict | None, user_intent: str | None) -> dict[str, Any]:
    top_candidates = candidate_pois[:2] if candidate_pois else SEED_POIS[:2]
    summary = "今天优先选择近距离、合规分高且风力较小的钓点。"
    if user_intent:
        summary = f"围绕“{user_intent}”来看，建议先确认规则和天气，再决定出钓点。"

    explanation = [
        "规则模型已经把禁钓、天气和距离放在前面，AI 只补充自然语言解释。",
        "如果你更看重路亚或新手练竿，可以把目标鱼或钓法继续输入给系统。",
    ]

    if recommendation and recommendation.get("items"):
        best = recommendation["items"][0]
        explanation.append(f"当前最优先点位是 {best['poi_name']}，综合分 {best['score']}。")

    tips = [
        "优先清晨或傍晚出钓。",
        "野钓点不要公开精确坐标。",
        "临水位置注意防滑和夜间照明。",
    ]

    return {
        "source": "mock",
        "summary": summary,
        "explanation": explanation,
        "top_recommendations": [
            {
                "poi_id": poi["id"],
                "poi_name": poi["name"],
                "reason": poi.get("reason") or "示例推荐理由",
                "risk": poi.get("risk") or "请结合现场规则判断。",
            }
            for poi in top_candidates
        ],
        "tips": tips,
    }


async def generate_fishing_advice(payload: dict) -> dict[str, Any]:
    user_intent = payload.get("user_intent")
    candidate_pois = payload.get("candidate_pois") or []
    recommendation = payload.get("recommendation")

    if settings.app_env == "production" and settings.deepseek_api_key:
        request_body = {
            "model": settings.deepseek_model,
            "messages": [
                {
                    "role": "system",
                    "content": "你是鱼你有图项目的出钓建议解释器，只解释规则模型的结果，不重新排序。",
                },
                {
                    "role": "user",
                    "content": {
                        "user_intent": user_intent,
                        "recommendation": recommendation,
                        "candidate_pois": candidate_pois,
                    },
                },
            ],
            "temperature": 0.2,
        }
        headers = {
            "Authorization": f"Bearer {settings.deepseek_api_key}",
            "Content-Type": "application/json",
        }
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.post(
                    f"{settings.deepseek_base_url}/chat/completions",
                    json=request_body,
                    headers=headers,
                )
                response.raise_for_status()
                payload = response.json()
                content = payload.get("choices", [{}])[0].get("message", {}).get("content")
                if isinstance(content, str) and content.strip():
                    return {
                        "source": "deepseek",
                        "summary": content.strip(),
                        "explanation": ["DeepSeek 生成的解释已返回。"],
                        "top_recommendations": _build_mock_advice(candidate_pois, recommendation, user_intent)["top_recommendations"],
                        "tips": ["请结合现场情况判断。"],
                    }
        except Exception:
            pass

    return _build_mock_advice(candidate_pois, recommendation, user_intent)
