from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_ai import router as ai_router
from app.api.routes_community import router as community_router
from app.api.routes_events import router as events_router
from app.api.routes_fish import router as fish_router
from app.api.routes_meta import router as meta_router
from app.api.routes_orders import router as orders_router
from app.api.routes_poi import router as poi_router
from app.api.routes_posts import router as posts_router
from app.api.routes_records import router as records_router
from app.api.routes_recommend import router as recommend_router
from app.api.routes_reports import router as reports_router
from app.api.routes_tutorials import router as tutorials_router
from app.api.routes_users import router as users_router
from app.api.routes_weather import router as weather_router
from app.core.config import settings


app = FastAPI(title=settings.app_name, version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_prefix = settings.api_prefix
app.include_router(meta_router, prefix=api_prefix)
app.include_router(orders_router, prefix=api_prefix)
app.include_router(poi_router, prefix=api_prefix)
app.include_router(posts_router, prefix=api_prefix)
app.include_router(records_router, prefix=api_prefix)
app.include_router(recommend_router, prefix=api_prefix)
app.include_router(reports_router, prefix=api_prefix)
app.include_router(users_router, prefix=api_prefix)
app.include_router(weather_router, prefix=api_prefix)
app.include_router(community_router, prefix=api_prefix)
app.include_router(events_router, prefix=api_prefix)
app.include_router(ai_router, prefix=api_prefix)
app.include_router(tutorials_router, prefix=api_prefix)
app.include_router(fish_router, prefix=api_prefix)
