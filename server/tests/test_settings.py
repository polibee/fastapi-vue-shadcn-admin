from server.app.core.config import Settings


def test_settings_snapshot_exposes_safe_runtime_configuration_only():
    from server.app.core.settings.schema import SettingsRead, build_settings_snapshot

    settings = Settings(
        app_name="Admin",
        environment="test",
        database_url="postgresql+asyncpg://secret-user:secret-pass@db/admin",
        redis_url="redis://:secret-pass@redis:6379/0",
        api_docs_enabled=False,
        jwt_secret="do-not-expose",
        jwt_access_token_minutes=45,
        task_lease_seconds=120,
    )

    snapshot = build_settings_snapshot(settings)

    assert snapshot == {
        "app_name": "Admin",
        "environment": "test",
        "api_docs_enabled": False,
        "jwt_access_token_minutes": 45,
        "task_lease_seconds": 120,
        "database_configured": True,
        "redis_configured": True,
    }
    assert set(SettingsRead.model_fields) == set(snapshot)
    assert "database_url" not in snapshot
    assert "redis_url" not in snapshot
    assert "jwt_secret" not in snapshot
