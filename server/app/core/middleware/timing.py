import time

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from server.app.core.telemetry import metrics


class TimingMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        started = time.perf_counter()

        async def send_with_timing(message: Message) -> None:
            if message["type"] == "http.response.start":
                duration_ms = max(0.0, (time.perf_counter() - started) * 1000)
                headers = list(message.get("headers", []))
                headers.append((b"x-response-time-ms", f"{duration_ms:.2f}".encode()))
                message = {**message, "headers": headers}
                scope.setdefault("state", {})["duration_ms"] = round(duration_ms, 2)
                metrics.increment("http.server.requests", tags={"method": scope.get("method", ""), "path": scope.get("path", "")})
                metrics.observe("http.server.duration_ms", duration_ms, tags={"method": scope.get("method", ""), "path": scope.get("path", "")})
            await send(message)

        await self.app(scope, receive, send_with_timing)
