from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    database_url: str
    supabase_jwt_secret: str
    cors_origins: str
    gemini_api_key: str


@lru_cache
def get_settings() -> Settings:
    return Settings()
