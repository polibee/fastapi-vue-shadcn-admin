import base64
import hashlib
import hmac
import json
import secrets
from datetime import datetime, timedelta, timezone

from server.app.core.config import get_settings
from server.app.core import auth_tokens

_HASH_ALGORITHM = "sha256"
_HASH_ITERATIONS = 310_000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(_HASH_ALGORITHM, password.encode(), salt, _HASH_ITERATIONS)
    return f"pbkdf2_{_HASH_ALGORITHM}${_HASH_ITERATIONS}${_b64encode(salt)}${_b64encode(digest)}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, iterations, salt, expected = encoded.split("$", 3)
        if scheme != f"pbkdf2_{_HASH_ALGORITHM}":
            return False
        actual = hashlib.pbkdf2_hmac(_HASH_ALGORITHM, password.encode(), _b64decode(salt), int(iterations))
        return hmac.compare_digest(_b64encode(actual), expected)
    except (TypeError, ValueError):
        return False


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    return _create_token(subject, "access", expires_minutes or get_settings().jwt_access_token_minutes)


def create_refresh_token(subject: str) -> str:
    return _create_token(subject, "refresh", get_settings().jwt_refresh_token_minutes)


def _create_token(subject: str, token_type: str, expires_minutes: int) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=expires_minutes)
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": subject, "iat": int(now.timestamp()), "exp": int(expires.timestamp()), "typ": token_type, "jti": secrets.token_urlsafe(18)}
    encoded_header = _b64encode(json.dumps(header, separators=(",", ":")).encode())
    encoded_payload = _b64encode(json.dumps(payload, separators=(",", ":")).encode())
    message = f"{encoded_header}.{encoded_payload}".encode()
    signature = hmac.new(settings.jwt_secret.encode(), message, hashlib.sha256).digest()
    return f"{encoded_header}.{encoded_payload}.{_b64encode(signature)}"


def decode_access_token(token: str) -> dict[str, object] | None:
    try:
        payload = _decode_signature(token)
        if payload.get("typ", "access") != "access":
            return None
        return payload
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None


async def decode_token(token: str, *, expected_type: str) -> dict[str, object]:
    payload = _decode_signature(token)
    if payload.get("typ") != expected_type:
        raise ValueError("invalid token type")
    token_id = payload.get("jti")
    if isinstance(token_id, str) and await auth_tokens.token_store.is_revoked(token_id):
        raise ValueError("revoked token")
    return payload


async def revoke_refresh_token(token: str) -> None:
    payload = await decode_token(token, expected_type="refresh")
    token_id = payload.get("jti")
    exp = payload.get("exp")
    if not isinstance(token_id, str) or not isinstance(exp, int):
        raise ValueError("invalid refresh token")
    await auth_tokens.token_store.revoke(token_id, auth_tokens.remaining_ttl(exp))


def _decode_signature(token: str) -> dict[str, object]:
    try:
        encoded_header, encoded_payload, encoded_signature = token.split(".", 2)
        message = f"{encoded_header}.{encoded_payload}".encode()
        expected = hmac.new(get_settings().jwt_secret.encode(), message, hashlib.sha256).digest()
        if not hmac.compare_digest(_b64decode(encoded_signature), expected):
            raise ValueError("invalid signature")
        payload = json.loads(_b64decode(encoded_payload))
        if int(payload["exp"]) <= int(datetime.now(timezone.utc).timestamp()):
            raise ValueError("expired token")
        if not payload.get("sub"):
            raise ValueError("missing subject")
        return payload
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise ValueError("invalid token") from error


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
