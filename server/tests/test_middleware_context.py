from fastapi import FastAPI, Request
from httpx import ASGITransport, AsyncClient
import pytest

from server.app.core.config import Settings
from server.app.core.context import get_request_context
from server.app.core.middleware.request_context import RequestContextMiddleware
from server.app.core.middleware.request_id import RequestIdMiddleware


def build_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(RequestIdMiddleware)

    @app.get("/context")
    async def context(request: Request):
        context = get_request_context(request)
        return {
            "request_id": context.request_id,
            "method": context.method,
            "path": context.path,
            "ip": context.ip,
            "user_agent": context.user_agent,
        }

    return app


@pytest.mark.asyncio
async def test_request_id_is_generated_and_returned_in_response() -> None:
    async with AsyncClient(transport=ASGITransport(app=build_app()), base_url="http://test") as client:
        response = await client.get("/context", headers={"User-Agent": "middleware-test"})

    assert response.status_code == 200
    request_id = response.headers["X-Request-ID"]
    assert request_id
    assert response.json()["request_id"] == request_id


@pytest.mark.asyncio
async def test_valid_incoming_request_id_is_preserved() -> None:
    request_id = "req-client-123"
    async with AsyncClient(transport=ASGITransport(app=build_app()), base_url="http://test") as client:
        response = await client.get("/context", headers={"X-Request-ID": request_id})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == request_id
    assert response.json()["request_id"] == request_id


@pytest.mark.asyncio
async def test_unsafe_incoming_request_id_is_replaced() -> None:
    async with AsyncClient(transport=ASGITransport(app=build_app()), base_url="http://test") as client:
        response = await client.get("/context", headers={"X-Request-ID": "bad\nvalue"})

    assert response.status_code == 200
    assert "\n" not in response.headers["X-Request-ID"]
    assert response.json()["request_id"] != "bad\nvalue"


@pytest.mark.asyncio
async def test_request_context_contains_connection_metadata() -> None:
    async with AsyncClient(transport=ASGITransport(app=build_app()), base_url="http://test") as client:
        response = await client.get("/context", headers={"User-Agent": "context-test"})

    body = response.json()
    assert body["method"] == "GET"
    assert body["path"] == "/context"
    assert body["user_agent"] == "context-test"
    assert body["ip"] == "127.0.0.1"


def test_middleware_settings_have_safe_defaults() -> None:
    settings = Settings()

    assert settings.request_id_header == "X-Request-ID"
    assert settings.cors_enabled is False
    assert settings.trusted_hosts_enabled is False
