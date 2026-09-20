from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.core.tasks.broker import publish_task
from .model import Task
from .events import record_task_event


async def recover_stale_running_tasks(session: AsyncSession, lease_seconds: int = 300, limit: int = 50) -> int:
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=lease_seconds)
    result = await session.execute(
        select(Task)
        .where(Task.status == "running", Task.started_at.is_not(None), Task.started_at < cutoff)
        .order_by(Task.id.asc())
        .limit(limit)
    )
    recovered = 0
    for task in result.scalars().all():
        task.started_at = None
        task.broker_job_id = None
        task.published_at = None
        task.updated_at = datetime.now(timezone.utc)
        if task.attempts >= task.max_attempts:
            task.status = "dead"
            task.error_message = "Worker lease expired after maximum attempts"
            task.message = "Task moved to dead after worker lease expired"
        else:
            task.status = "pending"
            task.error_message = "Worker lease expired; task queued for retry"
            task.message = "Recovered after worker lease expired"
        record_task_event(session, task, "recovered" if task.status == "pending" else "dead", task.message, status=task.status, progress=task.progress)
        recovered += 1

    if recovered:
        await session.commit()
    return recovered


async def recover_pending_tasks(session: AsyncSession, limit: int = 50) -> int:
    result = await session.execute(
        select(Task)
        .where(Task.status == "pending", Task.published_at.is_(None))
        .order_by(Task.id.asc())
        .limit(limit)
    )
    recovered = 0
    for task in result.scalars().all():
        try:
            broker_job_id = await publish_task(task.task_id, task.task_name)
        except Exception:
            continue
        if not broker_job_id:
            continue
        now = datetime.now(timezone.utc)
        task.broker_job_id = broker_job_id
        task.published_at = now
        task.updated_at = now
        record_task_event(session, task, "published", "Recovered pending task published", status=task.status, progress=task.progress)
        recovered += 1

    if recovered:
        await session.commit()
    return recovered
