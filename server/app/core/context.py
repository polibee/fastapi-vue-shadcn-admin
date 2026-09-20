from dataclasses import dataclass
from datetime import datetime

from fastapi import Request


@dataclass(frozen=True, slots=True)
class RequestContext:
    request_id: str
    trace_id: str | None
    user_id: int | None
    ip: str | None
    user_agent: str | None
    method: str
    path: str
    started_at: datetime


def get_request_context(request: Request) -> RequestContext:
    context = getattr(request.state, "request_context", None)
    if context is None:
        raise RuntimeError("request context middleware is not installed")
    return context
