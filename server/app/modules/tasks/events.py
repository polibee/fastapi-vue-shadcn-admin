from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from .model import Task, TaskEvent


def record_task_event(
    session: AsyncSession,
    task: Task,
    event_type: str,
    message: str | None = None,
    *,
    status: str | None = None,
    progress: int | None = None,
) -> TaskEvent:
    event = TaskEvent(
        task_id=task.id,
        event_type=event_type,
        message=message,
        status=status,
        progress=progress,
        created_at=datetime.now(timezone.utc),
    )
    session.add(event)
    return event
