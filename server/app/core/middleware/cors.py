from starlette.middleware.cors import CORSMiddleware as StarletteCORSMiddleware


class CORSMiddleware(StarletteCORSMiddleware):
    """Project boundary for the framework CORS middleware."""
