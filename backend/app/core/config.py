from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "鱼你有图"
    app_env: str = "development"
    api_prefix: str = "/api"

    amap_web_service_key: str = "0313792450ec0c2b6da97e552c438fab"
    amap_security_code: str = ""

    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"

    frontend_origin: str = "http://localhost:5173"
    frontend_origin_alt: str = "http://127.0.0.1:5173"

    default_city_code: str = "420100"
    default_city_name: str = "武汉市"

    def cors_origins(self) -> list[str]:
        return [self.frontend_origin, self.frontend_origin_alt]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
