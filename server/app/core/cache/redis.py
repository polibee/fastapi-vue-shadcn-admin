import json

from redis.asyncio import Redis

from server.app.core.config import get_settings


def _create_client() -> Redis | None:
    redis_url = get_settings().redis_url
    return Redis.from_url(redis_url) if redis_url else None


redis_client = _create_client()


async def check_redis() -> bool:
    if redis_client is None:
        return False
    try:
        return bool(await redis_client.ping())
    except Exception:
        return False


async def get_json(key: str):
    if redis_client is None:
        return None
    try:
        value = await redis_client.get(key)
        if value is None:
            return None
        return json.loads(value)
    except Exception:
        return None


async def set_json(key: str, value, ttl_seconds: int) -> bool:
    if redis_client is None:
        return False
    try:
        await redis_client.setex(key, ttl_seconds, json.dumps(value, separators=(",", ":")))
        return True
    except Exception:
        return False
