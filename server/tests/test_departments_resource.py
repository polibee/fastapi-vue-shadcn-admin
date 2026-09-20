import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_departments_manifest_and_crud_are_generic_resource_contract(session, admin_headers):
    from server.app.core.database.session import get_session
    from server.app.main import app

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            manifest = await client.get("/api/v1/admin/resources/departments", headers=admin_headers)
            assert manifest.status_code == 200
            assert manifest.json()["api"]["base"] == "/api/v1/departments"
            assert manifest.json()["query"]["searchFields"] == ["name", "code"]

            created = await client.post(
                "/api/v1/departments",
                json={"name": "Engineering", "code": "ENG", "description": "Platform team"},
                headers=admin_headers,
            )
            assert created.status_code == 201
            department_id = created.json()["id"]
            assert created.json()["is_active"] is True

            listed = await client.get("/api/v1/departments?search=ENG", headers=admin_headers)
            assert listed.status_code == 200
            assert listed.json()["total"] == 1

            updated = await client.put(
                f"/api/v1/departments/{department_id}",
                json={"name": "Platform Engineering", "code": "ENG", "description": "Core team", "is_active": False},
                headers=admin_headers,
            )
            assert updated.status_code == 200
            assert updated.json()["is_active"] is False

            deleted = await client.delete(f"/api/v1/departments/{department_id}", headers=admin_headers)
            assert deleted.status_code == 204
    finally:
        app.dependency_overrides.clear()


def test_departments_resource_definition_has_no_page_component_requirement():
    from server.app.core.resources.registry import get_resource_manifest

    manifest = get_resource_manifest("departments")
    assert manifest["routes"]["list"] == "/departments"
    assert manifest["permissions"] == {
        "view": "departments.view",
        "create": "departments.create",
        "update": "departments.update",
        "delete": "departments.delete",
    }
