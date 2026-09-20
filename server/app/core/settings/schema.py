from pydantic import BaseModel, ConfigDict

from server.app.core.config import Settings


class SettingsRead(BaseModel):
    model_config = ConfigDict(extra="forbid")

    app_name: str
    environment: str
    api_docs_enabled: bool
    jwt_access_token_minutes: int
    task_lease_seconds: int
    database_configured: bool
    redis_configured: bool


def build_settings_snapshot(settings: Settings) -> dict[str, object]:
    return {
        "app_name": settings.app_name,
        "environment": settings.environment,
        "api_docs_enabled": settings.api_docs_enabled,
        "jwt_access_token_minutes": settings.jwt_access_token_minutes,
        "task_lease_seconds": settings.task_lease_seconds,
        "database_configured": bool(settings.database_url),
        "redis_configured": bool(settings.redis_url),
    }
