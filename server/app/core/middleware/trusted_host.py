from starlette.middleware.trustedhost import TrustedHostMiddleware as StarletteTrustedHostMiddleware


class TrustedHostMiddleware(StarletteTrustedHostMiddleware):
    """Project boundary for host-header validation."""
