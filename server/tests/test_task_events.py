from datetime import datetime, timezone

import pytest
from sqlalchemy import select


@pytest.mark.asyncio
async def test_task_events_are_recorded_for_creation_and_publish(session, monkeypatch):
    from server.app.modules.tasks.events import record_task_event
    from server.app.modules.tasks.model import Task, TaskEvent

    now = datetime.now(timezone.utc)
    task = Task(
        task_id="event-task",
        task_name="demo.events",
        status="pending",
        payload_json="{}",
        request_id="request-events",
        created_at=now,
        updated_at=now,
    )
    session.add(task)
    await session.flush()
    record_task_event(session, task, "created", "Task created", status="pending", progress=0)
    record_task_event(session, task, "published", "Task published", status="pending", progress=0)
    await session.commit()

    events = (await session.scalars(select(TaskEvent).order_by(TaskEvent.id.asc()))).all()
    assert [(event.event_type, event.status) for event in events] == [
        ("created", "pending"),
        ("published", "pending"),
    ]


@pytest.mark.asyncio
async def test_task_timeline_endpoint_returns_events(session, admin_headers, monkeypatch):
    from httpx import ASGITransport, AsyncClient

    from server.app.main import app
    from server.app.core.database import session as database_session
    from server.app.modules.tasks.model import Task, TaskEvent

    now = datetime.now(timezone.utc)
    task = Task(
        task_id="timeline-task",
        task_name="demo.timeline",
        status="succeeded",
        progress=100,
        payload_json="{}",
        request_id="request-timeline",
        created_at=now,
        updated_at=now,
    )
    session.add(task)
    await session.flush()
    session.add(TaskEvent(task_id=task.id, event_type="succeeded", message="Completed", status="succeeded", progress=100, created_at=now))
    await session.commit()

    async def override_session():
        yield session

    app.dependency_overrides[database_session.get_session] = override_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/tasks/timeline-task/events", headers=admin_headers)
    finally:
        app.dependency_overrides.pop(database_session.get_session, None)

    assert response.status_code == 200
    assert response.json()["items"][0]["event_type"] == "succeeded"
