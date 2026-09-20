import pytest
from httpx import ASGITransport, AsyncClient

from server.app.core.auth import create_refresh_token, decode_token, revoke_refresh_token
from server.app.core.database.session import get_session
from server.app.core.auth_tokens import token_store
from server.app.core.auth import hash_password
from server.app.main import app
from server.app.modules.users.model import User


class FakeTokenStore:
    def __init__(self):
        self.revoked = {}

    async def revoke(self, token_id, ttl_seconds):
        self.revoked[token_id] = ttl_seconds

    async def is_revoked(self, token_id):
        return token_id in self.revoked


@pytest.mark.asyncio
async def test_refresh_token_can_be_rotated_and_revoked(monkeypatch) -> None:
    store = FakeTokenStore()
    monkeypatch.setattr("server.app.core.auth_tokens.token_store", store)
    token = create_refresh_token("7")

    payload = await decode_token(token, expected_type="refresh")
    assert payload["sub"] == "7"
    assert payload["typ"] == "refresh"

    await revoke_refresh_token(token)
    with pytest.raises(ValueError, match="revoked"):
        await decode_token(token, expected_type="refresh")


@pytest.mark.asyncio
async def test_login_returns_refresh_token_and_refresh_endpoint_rotates(session, monkeypatch):
    store = FakeTokenStore()
    monkeypatch.setattr("server.app.core.auth_tokens.token_store", store)
    session.add(User(username="admin", email="admin@example.test", password_hash=hash_password("secret")))
    await session.commit()

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            login = await client.post("/api/v1/auth/login", json={"username": "admin", "password": "secret"})
            assert login.status_code == 200
            refresh_token = login.json()["refresh_token"]

            refreshed = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
            assert refreshed.status_code == 200
            assert refreshed.json()["access_token"]
            assert refreshed.json()["refresh_token"] != refresh_token

            revoked = await client.post("/api/v1/auth/revoke", json={"refresh_token": refreshed.json()["refresh_token"]})
            assert revoked.status_code == 204
    finally:
        app.dependency_overrides.clear()
