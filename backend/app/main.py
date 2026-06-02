from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_ai import router as ai_router
from app.api.routes_fish import router as fish_router
from app.api.routes_meta import router as meta_router
from app.api.routes_poi import router as poi_router
from app.api.routes_posts import router as posts_router
from app.api.routes_recommend import router as recommend_router
from app.api.routes_tutorials import router as tutorials_router
from app.api.routes_weather import router as weather_router
from app.core.config import settings


app = FastAPI(title=settings.app_name, version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_prefix = settings.api_prefix
app.include_router(meta_router, prefix=api_prefix)
app.include_router(poi_router, prefix=api_prefix)
app.include_router(posts_router, prefix=api_prefix)
app.include_router(recommend_router, prefix=api_prefix)
app.include_router(weather_router, prefix=api_prefix)
app.include_router(ai_router, prefix=api_prefix)
app.include_router(tutorials_router, prefix=api_prefix)
app.include_router(fish_router, prefix=api_prefix)
