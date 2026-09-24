from datetime import datetime, timezone

import pytest


def test_worker_and_scheduler_refuse_to_start_without_redis(monkeypatch):
    from server.worker import tasks_worker

    monkeypatch.setattr(tasks_worker, "get_settings", lambda: type("Settings", (), {"redis_url": None})())

    with pytest.raises(RuntimeError, match="REDIS_URL"):
        tasks_worker.create_worker()
    with pytest.raises(RuntimeError, match="REDIS_URL"):
        tasks_worker.create_worker(scheduled_only=True)


@pytest.mark.asyncio
async def test_pending_task_stays_pending_when_redis_publish_fails(session, monkeypatch):
    from server.app.modules.tasks.model import Task
    from server.app.modules.tasks.recovery import recover_pending_tasks

    task = Task(
        task_id="redis-outage-task",
        task_name="demo.redis-outage",
        status="pending",
        payload_json="{}",
        request_id="request-redis-outage",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    session.add(task)
    await session.commit()

    async def unavailable_publish(*args, **kwargs):
        raise ConnectionError("redis unavailable")

    monkeypatch.setattr("server.app.modules.tasks.recovery.publish_task", unavailable_publish)

    assert await recover_pending_tasks(session) == 0
    await session.refresh(task)
    assert task.status == "pending"
    assert task.broker_job_id is None
    assert task.published_at is None
