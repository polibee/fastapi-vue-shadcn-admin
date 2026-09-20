from datetime import datetime, timezone

import pytest


@pytest.mark.asyncio
async def test_recovery_republishes_only_unpublished_pending_tasks(session, monkeypatch):
    from server.app.modules.tasks.model import Task
    from server.app.modules.tasks.recovery import recover_pending_tasks

    now = datetime.now(timezone.utc)
    deferred = Task(
        task_id="deferred-task",
        task_name="demo.deferred",
        status="pending",
        payload_json="{}",
        request_id="request-deferred",
        created_at=now,
        updated_at=now,
    )
    already_published = Task(
        task_id="published-task",
        task_name="demo.published",
        status="pending",
        payload_json="{}",
        request_id="request-published",
        broker_job_id="published-task",
        published_at=now,
        created_at=now,
        updated_at=now,
    )
    session.add_all([deferred, already_published])
    await session.commit()

    published: list[tuple[str, str]] = []

    async def fake_publish(task_id: str, task_name: str, job_id: str | None = None) -> str:
        published.append((task_id, task_name))
        return job_id or task_id

    monkeypatch.setattr("server.app.modules.tasks.recovery.publish_task", fake_publish)

    recovered = await recover_pending_tasks(session)

    assert recovered == 1
    assert published == [("deferred-task", "demo.deferred")]
    await session.refresh(deferred)
    assert deferred.broker_job_id == "deferred-task"
    assert deferred.published_at is not None


@pytest.mark.asyncio
async def test_recovery_requeues_stale_running_task_until_max_attempts(session):
    from datetime import timedelta

    from server.app.modules.tasks.model import Task
    from server.app.modules.tasks.recovery import recover_stale_running_tasks

    now = datetime.now(timezone.utc)
    retryable = Task(
        task_id="stale-retryable",
        task_name="demo.stale",
        status="running",
        attempts=1,
        max_attempts=3,
        started_at=now - timedelta(minutes=10),
        payload_json="{}",
        request_id="request-stale-1",
        created_at=now,
        updated_at=now,
    )
    terminal = Task(
        task_id="stale-terminal",
        task_name="demo.dead",
        status="running",
        attempts=3,
        max_attempts=3,
        started_at=now - timedelta(minutes=10),
        payload_json="{}",
        request_id="request-stale-2",
        created_at=now,
        updated_at=now,
    )
    session.add_all([retryable, terminal])
    await session.commit()

    recovered = await recover_stale_running_tasks(session, lease_seconds=60)

    assert recovered == 2
    await session.refresh(retryable)
    await session.refresh(terminal)
    assert retryable.status == "pending"
    assert retryable.started_at is None
    assert retryable.message == "Recovered after worker lease expired"
    assert terminal.status == "dead"
    assert terminal.error_message == "Worker lease expired after maximum attempts"
