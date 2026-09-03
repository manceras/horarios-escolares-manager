"""Application settings, loaded once from the environment."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "horarios"
    database_url: str = "sqlite:///./horarios.db"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 480
    cors_origins: list[str] = ["http://localhost:5173"]

    # Maximum wall-clock time a single solver run may take.
    solver_time_limit_seconds: float = 30.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
