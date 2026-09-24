import pytest

from server.app.core.config import Settings
from server.app.core.production_guard import ProductionConfigurationError


@pytest.mark.asyncio
async def test_demo_seed_is_rejected_in_production(monkeypatch):
    from server.scripts import seed_demo_admin as seed_module

    settings = Settings(environment="production", jwt_secret="a" * 48)
    monkeypatch.setattr(seed_module, "get_settings", lambda: settings)

    with pytest.raises(ProductionConfigurationError) as error:
        await seed_module.seed_demo_admin()

    assert error.value.code == "demo_seed_disabled_in_production"
