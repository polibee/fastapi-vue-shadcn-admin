import pytest


@pytest.mark.asyncio
async def test_resource_manifest_cache_falls_back_to_definitions(monkeypatch):
    from server.app.core.resources import registry

    writes = []
    async def fake_get_json(key):
        return None

    async def fake_set_json(key, value, ttl_seconds):
        writes.append((key, ttl_seconds))
        return True

    monkeypatch.setattr(registry, "get_json", fake_get_json)
    monkeypatch.setattr(registry, "set_json", fake_set_json)

    manifests = await registry.list_resource_manifests_cached()

    assert {manifest["name"] for manifest in manifests} == {"users", "roles", "departments"}
    assert writes == [("admin:resource-manifests:v3", 300)]


def test_resource_manifest_is_versioned_json_without_runtime_objects():
    from server.app.core.resources.registry import get_resource_manifest

    manifest = get_resource_manifest("users")

    assert manifest["schemaVersion"] == "1.0"
    assert manifest["name"] == "users"
    assert manifest["api"]["base"] == "/api/v1/users"
    assert all("model" not in value for value in manifest.values() if isinstance(value, dict))
    assert manifest["permissions"]["view"] == "users.view"
    assert manifest["query"] == {"searchFields": ["username", "email"], "filterFields": ["username", "is_active"], "sortFields": ["id", "username", "email"], "defaultSort": {"field": "id", "direction": "asc"}}
    assert {action["permission"] for action in manifest["actions"]} == {"users.update", "users.delete"}
    assert {action["icon"] for action in manifest["actions"]} == {"edit", "delete"}
    assert manifest["bulkActions"][0]["permission"] == "users.delete"
    assert "id" not in manifest["table"]["columns"]


def test_resource_registry_rejects_unknown_resource():
    from server.app.core.resources.registry import ResourceNotFoundError, get_resource_manifest

    with pytest.raises(ResourceNotFoundError):
        get_resource_manifest("unknown")


