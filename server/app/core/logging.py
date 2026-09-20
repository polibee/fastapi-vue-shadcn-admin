import json
import logging
from collections.abc import Mapping
from typing import Any


access_logger = logging.getLogger("admin.access")
access_logger.setLevel(logging.INFO)
if not access_logger.handlers:
    access_handler = logging.StreamHandler()
    access_handler.setFormatter(logging.Formatter("%(message)s"))
    access_logger.addHandler(access_handler)
SENSITIVE_KEYS = {"authorization", "cookie", "password", "secret", "token", "access_token", "refresh_token", "database_url", "redis_url"}


def _is_sensitive(key: str) -> bool:
    normalized = key.lower().replace("-", "_")
    return normalized in SENSITIVE_KEYS or normalized.endswith("_token") or normalized.endswith("_secret")


def sanitize_headers(headers: Mapping[str, str]) -> dict[str, str]:
    return {key: "[REDACTED]" if _is_sensitive(key) else value for key, value in headers.items()}


def sanitize_payload(payload: Any) -> Any:
    if isinstance(payload, Mapping):
        return {str(key): "[REDACTED]" if _is_sensitive(str(key)) else sanitize_payload(value) for key, value in payload.items()}
    if isinstance(payload, list):
        return [sanitize_payload(item) for item in payload]
    if isinstance(payload, tuple):
        return [sanitize_payload(item) for item in payload]
    return payload


def log_access(payload: Mapping[str, Any]) -> None:
    access_logger.info(json.dumps(sanitize_payload(dict(payload)), ensure_ascii=False, default=str, separators=(",", ":")))
