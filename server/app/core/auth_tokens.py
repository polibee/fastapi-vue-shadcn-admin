from datetime import datetime, timezone

from server.app.core.cache.redis import redis_client


class RedisTokenStore:
    async def revoke(self, token_id: str, ttl_seconds: int) -> None:
        if redis_client is not None:
            await redis_client.setex(f"admin:jwt:revoked:{token_id}", max(1, ttl_seconds), "1")

    async def is_revoked(self, token_id: str) -> bool:
        if redis_client is None:
            return False
        return bool(await redis_client.exists(f"admin:jwt:revoked:{token_id}"))


token_store = RedisTokenStore()


def remaining_ttl(exp: int) -> int:
    return max(1, exp - int(datetime.now(timezone.utc).timestamp()))
