import pytest
from fastapi import FastAPI, Request
from httpx import ASGITransport, AsyncClient, Response

from server.app.core.context import get_request_context
from server.app.core.middleware.request_context import RequestContextMiddleware
from server.app.core.middleware.request_id import RequestIdMiddleware
from server.app.core.telemetry import metrics
from server.app.core.http_client import HttpClient


def test_metrics_registry_counts_and_snapshots() -> None:
    metrics.reset()
    metrics.increment("demo.requests", tags={"route": "/demo"})
    metrics.observe("demo.duration_ms", 12.5, tags={"route": "/demo"})

    snapshot = metrics.snapshot()

    assert snapshot["counters"]["demo.requests|route=/demo"] == 1
    assert snapshot["histograms"]["demo.duration_ms|route=/demo"]["count"] == 1


@pytest.mark.asyncio
async def test_request_context_generates_trace_id_and_http_headers() -> None:
    app = FastAPI()
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(RequestIdMiddleware)

    @app.get("/context")
    async def context(request: Request):
        return {"trace_id": get_request_context(request).trace_id}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/context")

    assert response.status_code == 200
    assert response.headers["X-Trace-ID"] == response.json()["trace_id"]
    assert response.json()["trace_id"]


@pytest.mark.asyncio
async def test_http_client_propagates_correlation_headers() -> None:
    seen: dict[str, str] = {}

    async def handler(request):
        seen.update({key.lower(): value for key, value in request.headers.items()})
        return Response(200, json={"ok": True})

    client = HttpClient(transport=handler)
    response = await client.get("https://service.test/health", request_id="req-1", trace_id="trace-1")

    assert response.status_code == 200
    assert seen["x-request-id"] == "req-1"
    assert seen["x-trace-id"] == "trace-1"
