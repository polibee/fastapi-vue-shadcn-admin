from starlette.types import ASGIApp, Message, Receive, Scope, Send

from server.app.core.config import get_settings


SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}

PRODUCTION_CSP = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"


class SecurityHeadersMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_security_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                existing = {key.lower() for key, _ in headers}
                security_headers = dict(SECURITY_HEADERS)
                if get_settings().environment.lower() == "production":
                    security_headers["Content-Security-Policy"] = PRODUCTION_CSP
                    if scope.get("scheme") == "https":
                        security_headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
                headers.extend((name.lower().encode(), value.encode()) for name, value in security_headers.items() if name.lower().encode() not in existing)
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, send_with_security_headers)
