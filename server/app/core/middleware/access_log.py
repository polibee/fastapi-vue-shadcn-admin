from time import perf_counter

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from server.app.core.logging import log_access, sanitize_headers


class AccessLogMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        started = perf_counter()
        status_code = 500
        response_headers: dict[str, str] = {}

        async def capture_response(message: Message) -> None:
            nonlocal status_code, response_headers
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
                response_headers = {key.decode(): value.decode(errors="replace") for key, value in message.get("headers", [])}
            await send(message)

        try:
            await self.app(scope, receive, capture_response)
        finally:
            request_headers = {key.decode(): value.decode(errors="replace") for key, value in scope.get("headers", [])}
            state = scope.get("state", {})
            duration_ms = state.get("duration_ms", round((perf_counter() - started) * 1000, 2))
            log_access(
                {
                    "request_id": state.get("request_id"),
                    "trace_id": state.get("trace_id"),
                    "method": scope.get("method"),
                    "path": scope.get("path"),
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                    "headers": sanitize_headers(request_headers),
                    "response_headers": sanitize_headers(response_headers),
                }
            )
