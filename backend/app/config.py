"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI Disaster Response Management System"
    app_env: str = "development"
    debug: bool = True
    demo_mode: bool = True
    secret_key: str = "dev-secret-key-change-in-production"
    access_token_expire_minutes: int = 480
    algorithm: str = "HS256"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    # Matches Render / Netlify / Vercel preview & production hosts
    cors_origin_regex: str = r"https://.*\.(onrender\.com|vercel\.app|netlify\.app)"
    database_url: str = "sqlite:///./disaster_response.db"
    gdacs_api_url: str = ""
    usgs_api_url: str = ""
    ndma_api_url: str = ""
    osrm_api_url: str = ""
    ml_models_dir: str = "../ml/models"
    ml_results_dir: str = "../ml/results"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @property
    def external_apis_configured(self) -> bool:
        return bool(self.gdacs_api_url or self.usgs_api_url or self.ndma_api_url)


@lru_cache
def get_settings() -> Settings:
    return Settings()
