from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

from server.app.core.config import get_settings


async def publish_task(task_id: str, task_name: str, job_id: str | None = None) -> str | None:
    redis_url = get_settings().redis_url
    if not redis_url:
        return None
    pool: ArqRedis = await create_pool(RedisSettings.from_dsn(redis_url))
    try:
        job = await pool.enqueue_job("run_task", task_id, _job_id=job_id or task_id, _queue_name="background")
        return job.job_id if job else None
    finally:
        await pool.aclose()
