from dataclasses import dataclass
from hashlib import sha256

from fastapi import Depends, HTTPException, Request, status

from server.app.core.cache.redis import redis_client
from server.app.core.config import get_settings
from server.app.core.i18n import locale_from_request, translate
from server.app.core.auth import decode_access_token


class RateLimitExceeded(Exception):
    def __init__(self, retry_after: int) -> None:
        self.retry_after = retry_after
        super().__init__("rate limit exceeded")


class RateLimitUnavailable(Exception):
    pass


@dataclass(frozen=True, slots=True)
class RateLimitPolicy:
    name: str
    limit: int
    window_seconds: int


class RedisRateLimiter:
    def __init__(self, redis) -> None:
        self.redis = redis

    async def check(
        self,
        policy: RateLimitPolicy,
        *,
        identity: str,
        route: str | None = None,
        resource: str | None = None,
        action: str | None = None,
    ) -> int:
        if self.redis is None:
            raise RateLimitUnavailable()
        dimensions = ":".join(filter(None, (identity, route, resource, action)))
        digest = sha256(dimensions.encode()).hexdigest()[:24]
        key = f"admin:rate-limit:{policy.name}:{digest}"
        try:
            count = int(await self.redis.incr(key))
            if count == 1:
                await self.redis.expire(key, policy.window_seconds)
        except Exception as error:
            raise RateLimitUnavailable() from error
        if count > policy.limit:
            raise RateLimitExceeded(policy.window_seconds)
        return count


def api_rate_limit(resource: str):
    async def dependency(request: Request) -> None:
        settings = get_settings()
        policy = RateLimitPolicy("api", settings.api_rate_limit, settings.api_rate_window_seconds)
        user_id = getattr(request.state, "user_id", None)
        if user_id is None:
            authorization = request.headers.get("Authorization", "")
            if authorization.lower().startswith("bearer "):
                claims = decode_access_token(authorization[7:].strip())
                user_id = claims.get("sub") if claims else None
        identity = f"user:{user_id}" if user_id is not None else f"ip:{request.client.host if request.client else 'unknown'}"
        try:
            await RedisRateLimiter(redis_client).check(policy, identity=identity, route=request.url.path, resource=resource, action=request.method.lower())
        except RateLimitExceeded as error:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, headers={"Retry-After": str(error.retry_after)}, detail={"code": "rate_limited", "message": translate("errors", "rate_limited", locale_from_request(request))}) from error
        except RateLimitUnavailable:
            return

    return Depends(dependency)
