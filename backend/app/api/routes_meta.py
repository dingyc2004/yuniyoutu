from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {
        "ok": True,
        "service": settings.app_name,
        "app_env": settings.app_env,
        "amap_web_service_key_loaded": bool(settings.amap_web_service_key),
        "amap_js_api_key_loaded": bool(settings.amap_js_api_key),
        "amap_security_code_loaded": bool(settings.amap_security_code),
    }


@router.get("/amap/config")
async def amap_config() -> dict:
    return {
        "data": {
            "key": settings.amap_js_api_key,
            "securityCode": settings.amap_security_code,
            "ready": bool(settings.amap_js_api_key and settings.amap_security_code),
            "missing": [
                name
                for name, value in (
                    ("AMAP_JS_API_KEY", settings.amap_js_api_key),
                    ("AMAP_SECURITY_CODE", settings.amap_security_code),
                )
                if not value
            ],
        }
    }
