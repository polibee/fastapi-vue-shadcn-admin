from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "server/.env"), extra="ignore")

    app_name: str = "FastAPI Vue Admin"
    environment: str = "development"
    database_url: str | None = None
    redis_url: str | None = None
    api_docs_enabled: bool = True
    jwt_secret: str = "development-only-change-me"
    jwt_access_token_minutes: int = 60
    task_lease_seconds: int = 300
    request_id_header: str = "X-Request-ID"
    cors_enabled: bool = False
    cors_allow_origins: list[str] = []
    cors_allow_methods: list[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    cors_allow_headers: list[str] = ["Authorization", "Content-Type", "X-Request-ID"]
    cors_allow_credentials: bool = True
    trusted_hosts_enabled: bool = False
    trusted_hosts: list[str] = []
    jwt_refresh_token_minutes: int = 10080
    password_min_length: int = 8
    login_rate_limit: int = 5
    login_rate_window_seconds: int = 60
    api_rate_limit: int = 120
    api_rate_window_seconds: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
