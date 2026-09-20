from datetime import datetime, timezone

from arq import cron
from arq.connections import RedisSettings
from arq.worker import Worker
from server.app.core.config import get_settings
from sqlalchemy import select

from server.app.core.database.session import SessionFactory
from server.app.modules.tasks.model import Task
from server.app.modules.tasks.events import record_task_event
from server.app.modules.tasks.recovery import recover_pending_tasks, recover_stale_running_tasks
# Import all metadata-bearing models before the async session is used.
from server.app.modules.audit.model import AuditLog  # noqa: F401
from server.app.modules.permissions.model import Permission  # noqa: F401
from server.app.modules.roles.model import Role  # noqa: F401
from server.app.modules.users.model import User  # noqa: F401


async def run_task(ctx: dict, task_id: str) -> None:
    if SessionFactory is None:
        return
    async with SessionFactory() as session:
        task = await session.scalar(select(Task).where(Task.task_id == task_id))
        if task is None or task.status != "pending":
            return
        task.status = "running"
        task.attempts += 1
        task.progress = 10
        task.message = "Worker started"
        task.started_at = datetime.now(timezone.utc)
        task.error_message = None
        task.updated_at = task.started_at
        record_task_event(session, task, "started", task.message, status=task.status, progress=task.progress)
        await session.commit()
        if 'force_fail' in task.payload_json and 'true' in task.payload_json:
            task.status = "failed"
            task.message = "Task failed by development test flag"
            task.error_message = task.message
            task.started_at = None
            task.updated_at = datetime.now(timezone.utc)
            record_task_event(session, task, "failed", task.message, status=task.status, progress=task.progress)
            await session.commit()
            return
        task.status = "succeeded"
        task.progress = 100
        task.message = "Completed"
        task.started_at = None
        task.error_message = None
        task.updated_at = datetime.now(timezone.utc)
        record_task_event(session, task, "succeeded", task.message, status=task.status, progress=task.progress)
        await session.commit()


async def recover_tasks(ctx: dict) -> None:
    if SessionFactory is None:
        return
    async with SessionFactory() as session:
        await recover_stale_running_tasks(session, lease_seconds=get_settings().task_lease_seconds)
        await recover_pending_tasks(session)


def create_worker(*, scheduled_only: bool = False) -> Worker:
    settings = get_settings()
    if not settings.redis_url:
        raise RuntimeError("REDIS_URL must be configured to start the task worker")
    functions = [recover_tasks] if scheduled_only else [run_task, recover_tasks]
    return Worker(
        functions,
        queue_name="background",
        cron_jobs=[cron(recover_tasks, second={0, 30}, run_at_startup=True, name="recover-pending-tasks")],
        max_jobs=1 if scheduled_only else 4,
        redis_settings=RedisSettings.from_dsn(settings.redis_url),
    )


def run_worker() -> None:
    create_worker().run()


def run_scheduler() -> None:
    create_worker(scheduled_only=True).run()


if __name__ == "__main__":
    run_worker()
