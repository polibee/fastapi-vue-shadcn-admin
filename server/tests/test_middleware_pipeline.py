import logging

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_application_pipeline_adds_correlation_security_and_timing_headers(monkeypatch) -> None:
    from server.app.core.health import TaskQueueStats
    from server.app.main import app

    async def healthy_database():
        return True

    async def healthy_redis():
        return True

    async def empty_task_stats():
        return TaskQueueStats(total=0, pending=0, running=0, failed=0, dead=0)

    monkeypatch.setattr("server.app.core.health.check_database", healthy_database)
    monkeypatch.setattr("server.app.core.health.check_redis", healthy_redis)
    monkeypatch.setattr("server.app.core.health.get_task_stats", empty_task_stats)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health", headers={"X-Request-ID": "pipeline-1"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "pipeline-1"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert float(response.headers["X-Response-Time-ms"]) >= 0


@pytest.mark.asyncio
async def test_application_access_log_does_not_contain_credentials(monkeypatch, caplog) -> None:
    from server.app.core.health import TaskQueueStats
    from server.app.main import app

    async def empty_task_stats():
        return TaskQueueStats(total=0, pending=0, running=0, failed=0, dead=0)

    async def healthy_database():
        return True

    async def healthy_redis():
        return True

    monkeypatch.setattr("server.app.core.health.check_database", healthy_database)
    monkeypatch.setattr("server.app.core.health.check_redis", healthy_redis)
    monkeypatch.setattr("server.app.core.health.get_task_stats", empty_task_stats)
    caplog.set_level(logging.INFO, logger="admin.access")

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.get("/api/v1/health", headers={"Authorization": "Bearer dont-log-me"})

    assert "dont-log-me" not in " ".join(record.getMessage() for record in caplog.records if record.name == "admin.access")
