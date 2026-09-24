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


def test_resource_contract_separates_admin_route_and_api_base():
    from server.app.core.resources.definitions import RESOURCE_DEFINITIONS

    departments = RESOURCE_DEFINITIONS["departments"]
    assert departments.route == "/admin/departments"
    assert departments.api_base == "/api/v1/departments"


def test_resource_contract_rejects_mixed_route_namespaces():
    from server.app.core.resources.contract import ResourceDefinition, validate_route_boundary

    invalid_ui_route = ResourceDefinition(name="demo", label="demo", label_plural="demo", api_base="/api/v1/demo", route="/demo", permissions={})
    invalid_api_base = ResourceDefinition(name="demo", label="demo", label_plural="demo", api_base="/demo", route="/admin/demo", permissions={})

    with pytest.raises(ValueError, match="UI route"):
        validate_route_boundary(invalid_ui_route)
    with pytest.raises(ValueError, match="API base"):
        validate_route_boundary(invalid_api_base)


