import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select


@pytest.mark.asyncio
async def test_permission_catalog_is_protected_and_sorted(session, admin_headers):
    from server.app.core.database.session import get_session
    from server.app.main import app

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/permissions", headers=admin_headers)
            assert response.status_code == 200
            body = response.json()
            assert body["total"] == len(body["items"])
            assert [item["code"] for item in body["items"]] == sorted(item["code"] for item in body["items"])
            assert "users.view" in {item["code"] for item in body["items"]}
            scope = await client.put("/api/v1/roles/1/data-scope", json={"data_scope": "self"}, headers=admin_headers)
            assert scope.status_code == 200
            assert scope.json()["data_scope"] == "self"

            from server.app.modules.roles.model import Role
            administrator = await session.scalar(select(Role).where(Role.name == "test-administrator"))
            assert administrator is not None
            administrator.data_scope = "self"
            await session.flush()
            denied = await client.delete("/api/v1/users/999", headers=admin_headers)
            assert denied.status_code == 403
            assert denied.json()["code"] == "data_scope_denied"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_administrator_role_keeps_all_permissions_when_permissions_are_updated(session, admin_headers):
    from server.app.core.database.session import get_session
    from server.app.main import app
    from server.app.modules.permissions.model import Permission
    from server.app.modules.roles.model import Role

    async def override_session():
        yield session

    users_view = await session.scalar(select(Permission).where(Permission.code == "users.view"))
    assert users_view is not None
    administrator = Role(name="administrator", permissions=[users_view])
    session.add(administrator)
    await session.flush()
    roles_view = await session.scalar(select(Permission).where(Permission.code == "roles.view"))
    assert roles_view is not None
    app.dependency_overrides[get_session] = override_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.put("/api/v1/roles/%s/permissions" % administrator.id, json={"codes": ["users.view"]}, headers=admin_headers)
            assert response.status_code == 200
            expected = sorted((await session.scalars(select(Permission).order_by(Permission.code.asc()))).all(), key=lambda item: item.code)
            assert response.json()["permissions"] == [item.code for item in expected]
    finally:
        app.dependency_overrides.clear()
