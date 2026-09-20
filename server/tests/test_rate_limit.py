import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from server.app.core.rate_limit import RateLimitExceeded, RateLimitPolicy, RedisRateLimiter, api_rate_limit


class FakeRedis:
    def __init__(self):
        self.values = {}
        self.expirations = {}

    async def incr(self, key):
        self.values[key] = self.values.get(key, 0) + 1
        return self.values[key]

    async def expire(self, key, ttl):
        self.expirations[key] = ttl
        return True


@pytest.mark.asyncio
async def test_rate_limiter_allows_requests_until_limit_then_rejects() -> None:
    limiter = RedisRateLimiter(FakeRedis())
    policy = RateLimitPolicy(name="login", limit=2, window_seconds=60)

    assert await limiter.check(policy, identity="ip:127.0.0.1") == 1
    assert await limiter.check(policy, identity="ip:127.0.0.1") == 2
    with pytest.raises(RateLimitExceeded) as error:
        await limiter.check(policy, identity="ip:127.0.0.1")

    assert error.value.retry_after == 60


@pytest.mark.asyncio
async def test_rate_limiter_uses_distinct_route_and_identity_keys() -> None:
    redis = FakeRedis()
    limiter = RedisRateLimiter(redis)
    policy = RateLimitPolicy(name="api", limit=1, window_seconds=30)

    await limiter.check(policy, identity="user:1", route="/users", action="list")
    await limiter.check(policy, identity="user:1", route="/roles", action="list")

    assert len(redis.values) == 2
    assert all(value == 1 for value in redis.values.values())


@pytest.mark.asyncio
async def test_api_rate_limit_dependency_returns_retry_after(monkeypatch) -> None:
    from server.app.core.config import get_settings
    import server.app.core.rate_limit as rate_limit_module

    redis = FakeRedis()
    settings = get_settings()
    monkeypatch.setattr(settings, "api_rate_limit", 1)
    monkeypatch.setattr(settings, "api_rate_window_seconds", 45)
    monkeypatch.setattr(rate_limit_module, "redis_client", redis)
    app = FastAPI()
    app.add_api_route("/users", lambda: {"ok": True}, dependencies=[api_rate_limit("users")])

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        assert (await client.get("/users")).status_code == 200
        response = await client.get("/users")

    assert response.status_code == 429
    assert response.headers["Retry-After"] == "45"
