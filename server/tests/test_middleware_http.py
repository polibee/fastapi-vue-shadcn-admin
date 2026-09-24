import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from server.app.core.middleware.cors import CORSMiddleware
from server.app.core.middleware.security_headers import SecurityHeadersMiddleware
from server.app.core.middleware.trusted_host import TrustedHostMiddleware


def build_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://admin.example.test"],
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
        allow_credentials=True,
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["test", "localhost"])

    @app.get("/public")
    async def public():
        return {"ok": True}

    return app


@pytest.mark.asyncio
async def test_security_headers_are_present() -> None:
    async with AsyncClient(transport=ASGITransport(app=build_app()), base_url="http://test") as client:
        response = await client.get("/public")

    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert response.headers["Permissions-Policy"] == "camera=(), microphone=(), geolocation=()"


@pytest.mark.asyncio
async def test_production_security_headers_include_csp_and_https_hsts(monkeypatch) -> None:
    from server.app.core.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "environment", "production")
    async with AsyncClient(transport=ASGITransport(app=build_app()), base_url="https://test") as client:
        response = await client.get("/public")

    assert response.headers["Content-Security-Policy"] == "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
    assert "max-age=" in response.headers["Strict-Transport-Security"]
    assert "unsafe-eval" not in response.headers["Content-Security-Policy"]


@pytest.mark.asyncio
async def test_cors_preflight_is_configured() -> None:
    async with AsyncClient(transport=ASGITransport(app=build_app()), base_url="http://test") as client:
        response = await client.options(
            "/public",
            headers={
                "Origin": "https://admin.example.test",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Authorization",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://admin.example.test"
    assert response.headers["access-control-allow-credentials"] == "true"


@pytest.mark.asyncio
async def test_trusted_host_rejects_unknown_host() -> None:
    async with AsyncClient(transport=ASGITransport(app=build_app()), base_url="http://evil.example") as client:
        response = await client.get("/public")

    assert response.status_code == 400
