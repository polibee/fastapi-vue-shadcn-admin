from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from scalar_fastapi import get_scalar_api_reference

from server.app.core.config import get_settings
from server.app.core.middleware.access_log import AccessLogMiddleware
from server.app.core.middleware.cors import CORSMiddleware
from server.app.core.middleware.request_context import RequestContextMiddleware
from server.app.core.middleware.request_id import RequestIdMiddleware
from server.app.core.middleware.security_headers import SecurityHeadersMiddleware
from server.app.core.middleware.timing import TimingMiddleware
from server.app.core.middleware.trusted_host import TrustedHostMiddleware
from server.app.core.modules import builtin_registry
from server.app.core.health import router as health_router
from server.app.core.database.session import DatabaseNotConfiguredError
from server.app.modules.roles.router import router as roles_router
from server.app.modules.users.router import router as users_router
from server.app.modules.auth.router import router as auth_router
from server.app.modules.audit.router import router as audit_router
from server.app.modules.tasks.router import router as tasks_router
from server.app.modules.permissions.router import router as permissions_router
from server.app.core.resources.router import router as resources_router
from server.app.core.settings.router import router as settings_router
from server.app.core.introspection_router import router as introspection_router
from server.app.core.generator.router import router as generator_router
from server.app.core.i18n import locale_from_request, translate

settings = get_settings()


@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.module_registry.boot_all()
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", docs_url=None, redoc_url=None, lifespan=lifespan)
app.state.module_registry = builtin_registry()
app.state.module_registry.register_all()

app.add_middleware(SecurityHeadersMiddleware)
if settings.cors_enabled:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
        allow_credentials=settings.cors_allow_credentials,
    )
if settings.trusted_hosts_enabled:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)
app.add_middleware(AccessLogMiddleware)
app.add_middleware(TimingMiddleware)
app.add_middleware(RequestContextMiddleware)
app.add_middleware(RequestIdMiddleware)

app.include_router(health_router)
app.include_router(users_router)
app.include_router(roles_router)
app.include_router(auth_router)
app.include_router(audit_router)
app.include_router(tasks_router)
app.include_router(permissions_router)
app.include_router(resources_router)
app.include_router(settings_router)
app.include_router(introspection_router)
app.include_router(generator_router)


@app.exception_handler(DatabaseNotConfiguredError)
async def database_not_configured(request: Request, __: DatabaseNotConfiguredError) -> JSONResponse:
    locale = locale_from_request(request)
    return JSONResponse(status_code=503, content={"code": "database_not_configured", "message": translate("errors", "database_not_configured", locale)})


@app.exception_handler(HTTPException)
async def http_error(request: Request, error: HTTPException) -> JSONResponse:
    headers = dict(error.headers or {})
    if isinstance(error.detail, dict) and "code" in error.detail:
        return JSONResponse(status_code=error.status_code, content=error.detail, headers=headers)
    locale = locale_from_request(request)
    return JSONResponse(status_code=error.status_code, content={"code": "http_error", "message": translate("errors", "http_error", locale)}, headers=headers)


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, error: RequestValidationError) -> JSONResponse:
    locale = locale_from_request(request)
    return JSONResponse(status_code=422, content={"code": "validation_error", "message": translate("errors", "request_validation_failed", locale), "details": error.errors()})


if settings.api_docs_enabled:
    @app.get("/docs/scalar", include_in_schema=False)
    async def scalar_docs():
        return get_scalar_api_reference(openapi_url=app.openapi_url, title=app.title)
