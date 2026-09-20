from uuid import uuid4

from starlette.types import ASGIApp, Message, Receive, Scope, Send


REQUEST_ID_HEADER = "X-Request-ID"
MAX_REQUEST_ID_LENGTH = 128


def _is_safe_request_id(value: str) -> bool:
    return bool(value) and len(value) <= MAX_REQUEST_ID_LENGTH and "\r" not in value and "\n" not in value


def ensure_request_id(request) -> str:
    incoming = request.headers.get(REQUEST_ID_HEADER, "").strip()
    request_id = incoming if _is_safe_request_id(incoming) else str(uuid4())
    request.state.request_id = request_id
    return request_id


class RequestIdMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        from starlette.requests import Request

        request = Request(scope, receive=receive)
        request_id = ensure_request_id(request)

        async def send_with_request_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((REQUEST_ID_HEADER.lower().encode(), request_id.encode()))
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, send_with_request_id)
