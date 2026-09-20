from collections.abc import Callable
from typing import Any

import httpx


class HttpClient:
    def __init__(self, *, timeout: float = 10.0, transport: Any = None, headers: dict[str, str] | None = None) -> None:
        if callable(transport):
            transport = httpx.MockTransport(transport)
        self._client = httpx.AsyncClient(timeout=timeout, transport=transport, headers=headers)

    async def request(self, method: str, url: str, *, request_id: str | None = None, trace_id: str | None = None, **kwargs: Any) -> httpx.Response:
        headers = dict(kwargs.pop("headers", {}) or {})
        if request_id:
            headers["X-Request-ID"] = request_id
        if trace_id:
            headers["X-Trace-ID"] = trace_id
        return await self._client.request(method, url, headers=headers, **kwargs)

    async def get(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self.request("POST", url, **kwargs)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "HttpClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()
