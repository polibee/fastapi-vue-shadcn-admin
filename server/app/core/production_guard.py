from server.app.core.config import Settings


class ProductionConfigurationError(RuntimeError):
    def __init__(self, code: str, fields: tuple[str, ...] = ()) -> None:
        self.code = code
        self.fields = fields
        super().__init__(code)


def validate_production_settings(settings: Settings) -> None:
    if settings.environment.lower() != "production":
        return
    if not settings.database_url:
        raise ProductionConfigurationError("database_not_configured", ("DATABASE_URL",))
    if not settings.redis_url:
        raise ProductionConfigurationError("redis_not_configured", ("REDIS_URL",))
    if not settings.jwt_secret or settings.jwt_secret == "development-only-change-me" or len(settings.jwt_secret) < 32:
        raise ProductionConfigurationError("insecure_jwt_secret", ("JWT_SECRET",))
    if not settings.trusted_hosts_enabled or not settings.trusted_hosts:
        raise ProductionConfigurationError("trusted_hosts_not_configured", ("TRUSTED_HOSTS",))
    if settings.api_docs_enabled:
        raise ProductionConfigurationError("api_docs_enabled_in_production", ("API_DOCS_ENABLED",))
