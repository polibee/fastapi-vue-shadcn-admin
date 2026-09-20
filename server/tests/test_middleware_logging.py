import json
import logging

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from server.app.core.middleware.access_log import AccessLogMiddleware
from server.app.core.middleware.timing import TimingMiddleware
from server.app.core.logging import sanitize_headers, sanitize_payload


def build_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(AccessLogMiddleware)
    app.add_middleware(TimingMiddleware)

    @app.post("/log")
    async def log_endpoint():
        return {"ok": True}

    return app


def test_sensitive_headers_are_redacted() -> None:
    result = sanitize_headers(
        {"Authorization": "Bearer secret", "Cookie": "session=secret", "X-Request-ID": "req-1", "Content-Type": "application/json"}
    )

    assert result["Authorization"] == "[REDACTED]"
    assert result["Cookie"] == "[REDACTED]"
    assert result["X-Request-ID"] == "req-1"
    assert result["Content-Type"] == "application/json"


def test_sensitive_payload_keys_are_redacted_recursively() -> None:
    result = sanitize_payload({"username": "admin", "password": "secret", "nested": {"access_token": "token"}})

    assert result == {"username": "admin", "password": "[REDACTED]", "nested": {"access_token": "[REDACTED]"}}


@pytest.mark.asyncio
async def test_access_log_is_json_and_timing_header_is_present(caplog) -> None:
    caplog.set_level(logging.INFO, logger="admin.access")

    async with AsyncClient(transport=ASGITransport(app=build_app()), base_url="http://test") as client:
        response = await client.post("/log", headers={"Authorization": "Bearer secret"}, json={"password": "secret"})

    assert response.status_code == 200
    assert "X-Response-Time-ms" in response.headers
    record = next(item for item in caplog.records if item.name == "admin.access")
    payload = json.loads(record.getMessage())
    assert payload["method"] == "POST"
    assert payload["path"] == "/log"
    assert payload["status_code"] == 200
    assert payload["duration_ms"] >= 0
    assert payload["headers"]["authorization"] == "[REDACTED]"
