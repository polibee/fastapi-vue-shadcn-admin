from datetime import datetime, timezone
from uuid import uuid4

from starlette.types import ASGIApp, Receive, Scope, Send

from server.app.core.context import RequestContext


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        from starlette.requests import Request

        request = Request(scope, receive=receive)
        client = request.client
        trace_id = request.headers.get("X-Trace-ID") or str(uuid4())
        request.state.trace_id = trace_id
        request.state.request_context = RequestContext(
            request_id=getattr(request.state, "request_id", ""),
            trace_id=trace_id,
            user_id=None,
            ip=client.host if client else None,
            user_agent=request.headers.get("User-Agent"),
            method=request.method,
            path=request.url.path,
            started_at=datetime.now(timezone.utc),
        )
        async def send_with_trace_id(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-trace-id", trace_id.encode()))
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, send_with_trace_id)
