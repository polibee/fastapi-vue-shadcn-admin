import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.anyio
async def test_health_reports_database_and_redis_status(monkeypatch):
    from server.app.main import app

    async def healthy_database():
        return True

    async def healthy_redis():
        return True

    monkeypatch.setattr("server.app.core.health.check_database", healthy_database)
    monkeypatch.setattr("server.app.core.health.check_redis", healthy_redis)
    from server.app.core.health import TaskQueueStats

    async def empty_task_stats():
        return TaskQueueStats(total=0, pending=0, running=0, failed=0, dead=0)

    monkeypatch.setattr("server.app.core.health.get_task_stats", empty_task_stats)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "database": {"status": "up"},
        "redis": {"status": "up"},
        "tasks": {"total": 0, "pending": 0, "running": 0, "failed": 0, "dead": 0},
    }


@pytest.mark.anyio
async def test_health_degrades_without_optional_dependencies(monkeypatch):
    from server.app.main import app

    async def unavailable_database():
        return False

    async def unavailable_redis():
        return False

    monkeypatch.setattr("server.app.core.health.check_database", unavailable_database)
    monkeypatch.setattr("server.app.core.health.check_redis", unavailable_redis)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "degraded"
    assert response.json()["database"]["status"] == "down"
    assert response.json()["redis"]["status"] == "down"
    assert response.json()["tasks"]["total"] >= 0


@pytest.mark.anyio
async def test_health_does_not_expose_connection_details(monkeypatch):
    from server.app.main import app

    async def raising_database():
        raise RuntimeError("postgresql://admin:secret@example.test:5432/app")

    async def raising_redis():
        raise RuntimeError("redis://:secret@example.test:6379/0")

    monkeypatch.setattr("server.app.core.health.check_database", raising_database)
    monkeypatch.setattr("server.app.core.health.check_redis", raising_redis)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/health")

    body = response.text
    assert response.status_code == 200
    assert "secret" not in body
    assert "example.test" not in body
