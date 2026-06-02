from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {
        "ok": True,
        "service": settings.app_name,
        "app_env": settings.app_env,
        "amap_key_loaded": bool(settings.amap_web_service_key),
    }


@router.get("/amap/config")
async def amap_config() -> dict:
    return {
        "data": {
            "key": settings.amap_web_service_key,
            "securityCode": settings.amap_security_code,
        }
    }
