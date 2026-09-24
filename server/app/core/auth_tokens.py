from datetime import datetime, timezone

from server.app.core.cache.redis import redis_client
from server.app.core.config import get_settings


class RedisSecurityStateUnavailable(RuntimeError):
    code = "security_state_unavailable"


class RedisTokenStore:
    async def revoke(self, token_id: str, ttl_seconds: int) -> None:
        if redis_client is None:
            if get_settings().environment.lower() == "production":
                raise RedisSecurityStateUnavailable
            return
        try:
            await redis_client.setex(f"admin:jwt:revoked:{token_id}", max(1, ttl_seconds), "1")
        except Exception as error:
            if get_settings().environment.lower() == "production":
                raise RedisSecurityStateUnavailable from error

    async def is_revoked(self, token_id: str) -> bool:
        if redis_client is None:
            if get_settings().environment.lower() == "production":
                raise RedisSecurityStateUnavailable
            return False
        try:
            return bool(await redis_client.exists(f"admin:jwt:revoked:{token_id}"))
        except Exception as error:
            if get_settings().environment.lower() == "production":
                raise RedisSecurityStateUnavailable from error
            return False


token_store = RedisTokenStore()


def remaining_ttl(exp: int) -> int:
    return max(1, exp - int(datetime.now(timezone.utc).timestamp()))
