import pytest
from httpx import ASGITransport, AsyncClient

from server.app.core.auth import hash_password
from server.app.core.database.session import get_session
from server.app.main import app
from server.app.modules.users.model import User
from server.app.modules.roles.model import Permission, Role


@pytest.mark.asyncio
async def test_login_returns_bearer_token_and_me_returns_safe_user(session):
    session.add(User(username="admin", email="admin@example.test", password_hash=hash_password("secret")))
    await session.commit()

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            login = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "secret"})
            assert login.status_code == 200
            body = login.json()
            assert body["token_type"] == "bearer"
            assert body["access_token"]

            current = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
            assert current.status_code == 200
            assert current.json() == {"id": 1, "username": "admin", "email": "admin@example.test", "is_active": True, "permissions": []}
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_current_user_includes_permissions_granted_by_roles(session):
    permission = Permission(code="users.view", description="View users")
    role = Role(name="administrator", permissions=[permission])
    user = User(username="admin", email="admin@example.test", password_hash=hash_password("secret"), roles=[role])
    session.add(user)
    await session.commit()

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            login = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "secret"})
            current = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {login.json()['access_token']}"})
            assert current.json()["permissions"] == ["users.view"]
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_login_rejects_invalid_password(session):
    session.add(User(username="admin", email="admin@example.test", password_hash=hash_password("secret")))
    await session.commit()

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "wrong"})
            assert response.status_code == 401
            assert response.json()["code"] == "invalid_credentials"
    finally:
        app.dependency_overrides.clear()
