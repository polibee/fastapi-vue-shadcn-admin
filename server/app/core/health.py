from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import func, select, text

from server.app.core.cache.redis import check_redis
from server.app.core.database.session import SessionFactory, engine
from server.app.modules.tasks.model import Task

router = APIRouter(prefix="/api/v1", tags=["Health"])


class DependencyStatus(BaseModel):
    status: str


class HealthResponse(BaseModel):
    status: str
    database: DependencyStatus
    redis: DependencyStatus
    tasks: "TaskQueueStats"


class TaskQueueStats(BaseModel):
    total: int
    pending: int
    running: int
    failed: int
    dead: int


async def check_database() -> bool:
    if engine is None:
        return False
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    database_up, redis_up = await _safe_checks()
    task_stats = await get_task_stats()
    overall = "ok" if database_up and redis_up else "degraded"
    return HealthResponse(
        status=overall,
        database=DependencyStatus(status="up" if database_up else "down"),
        redis=DependencyStatus(status="up" if redis_up else "down"),
        tasks=task_stats,
    )


async def get_task_stats() -> TaskQueueStats:
    empty = TaskQueueStats(total=0, pending=0, running=0, failed=0, dead=0)
    if SessionFactory is None:
        return empty
    try:
        async with SessionFactory() as session:
            rows = (await session.execute(select(Task.status, func.count()).group_by(Task.status))).all()
        counts = {status: int(count) for status, count in rows}
        return TaskQueueStats(
            total=sum(counts.values()),
            pending=counts.get("pending", 0),
            running=counts.get("running", 0),
            failed=counts.get("failed", 0),
            dead=counts.get("dead", 0),
        )
    except Exception:
        return empty


async def _safe_checks() -> tuple[bool, bool]:
    async def safe_check(check) -> bool:
        try:
            return bool(await check())
        except Exception:
            return False

    return await safe_check(check_database), await safe_check(check_redis)
