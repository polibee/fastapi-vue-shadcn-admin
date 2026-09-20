import json

import pytest


class FakeRedis:
    def __init__(self, value=None, fail=False):
        self.value = value
        self.fail = fail
        self.writes = []

    async def get(self, key):
        if self.fail:
            raise RuntimeError("redis unavailable")
        return self.value

    async def setex(self, key, ttl, value):
        if self.fail:
            raise RuntimeError("redis unavailable")
        self.writes.append((key, ttl, value))


@pytest.mark.asyncio
async def test_json_cache_reads_and_writes_without_exposing_redis_errors(monkeypatch):
    from server.app.core.cache import redis as cache

    client = FakeRedis()
    monkeypatch.setattr(cache, "redis_client", client)

    assert await cache.get_json("key") is None
    assert await cache.set_json("key", {"items": [1]}, ttl_seconds=30) is True
    assert client.writes == [("key", 30, json.dumps({"items": [1]}, separators=(",", ":")))]


@pytest.mark.asyncio
async def test_json_cache_degrades_to_miss_when_redis_is_unavailable(monkeypatch):
    from server.app.core.cache import redis as cache

    monkeypatch.setattr(cache, "redis_client", FakeRedis(fail=True))

    assert await cache.get_json("key") is None
    assert await cache.set_json("key", {"items": [1]}, ttl_seconds=30) is False
