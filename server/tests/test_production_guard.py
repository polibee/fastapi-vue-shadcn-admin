import pytest

from server.app.core.config import Settings
from server.app.core.production_guard import ProductionConfigurationError, validate_production_settings


def production_settings(**overrides):
    values = {
        "environment": "production",
        "database_url": "postgresql+asyncpg://app:secret@db/app",
        "redis_url": "redis://redis:6379/0",
        "jwt_secret": "a" * 48,
        "trusted_hosts_enabled": True,
        "trusted_hosts": ["admin.example.com"],
        "api_docs_enabled": False,
    }
    values.update(overrides)
    return Settings(**values)


def test_production_settings_accept_secure_configuration():
    validate_production_settings(production_settings())


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("jwt_secret", "development-only-change-me", "insecure_jwt_secret"),
        ("database_url", None, "database_not_configured"),
        ("redis_url", None, "redis_not_configured"),
        ("trusted_hosts_enabled", False, "trusted_hosts_not_configured"),
        ("trusted_hosts", [], "trusted_hosts_not_configured"),
        ("api_docs_enabled", True, "api_docs_enabled_in_production"),
    ],
)
def test_production_settings_reject_unsafe_configuration(field, value, code):
    settings = production_settings(**{field: value})
    with pytest.raises(ProductionConfigurationError) as error:
        validate_production_settings(settings)
    assert error.value.code == code
    assert "development-only-change-me" not in str(error.value)
    assert "a" * 48 not in str(error.value)
