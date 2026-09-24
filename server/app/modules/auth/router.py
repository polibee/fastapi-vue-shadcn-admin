from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from server.app.core.auth import create_access_token, create_refresh_token, decode_access_token, decode_token, revoke_refresh_token, verify_password
from server.app.core.auth_tokens import RedisSecurityStateUnavailable
from server.app.core.cache.redis import redis_client
from server.app.core.config import get_settings
from server.app.core.rate_limit import RateLimitExceeded, RateLimitUnavailable, RateLimitPolicy, RedisRateLimiter
from server.app.core.database.session import get_session
from server.app.core.i18n import locale_from_request, translate
from server.app.modules.users.model import User
from server.app.modules.users.repository import UserRepository
from .schema import CurrentUserRead, LoginRequest, RefreshRequest, RevokeRequest, TokenResponse

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
bearer_scheme = HTTPBearer(auto_error=False)


def auth_error(request: Request, code: str, status_code: int = status.HTTP_401_UNAUTHORIZED) -> HTTPException:
    locale = locale_from_request(request)
    return HTTPException(status_code=status_code, headers={"WWW-Authenticate": "Bearer"}, detail={"code": code, "message": translate("modules/auth", code, locale)})


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise auth_error(request, "authentication_required")
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise auth_error(request, "invalid_token")
    user = await UserRepository(session).get_by_id(int(payload["sub"]))
    if user is None or not user.is_active:
        raise auth_error(request, "invalid_token")
    request.state.user_id = user.id
    return user


@router.post("/login", response_model=TokenResponse)
async def login(request: Request, payload: LoginRequest, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    try:
        await RedisRateLimiter(redis_client).check(
            RateLimitPolicy("login", get_settings().login_rate_limit, get_settings().login_rate_window_seconds),
            identity=f"ip:{request.client.host if request.client else 'unknown'}:username:{payload.username.lower()}",
            route="/api/v1/auth/login",
            action="login",
        )
    except RateLimitExceeded as error:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            headers={"Retry-After": str(error.retry_after)},
            detail={"code": "login_rate_limited", "message": translate("modules/auth", "login_rate_limited", locale_from_request(request))},
        ) from error
    except RateLimitUnavailable:
        if get_settings().environment.lower() == "production":
            raise HTTPException(status_code=503, detail={"code": "security_state_unavailable", "message": translate("errors", "security_state_unavailable", locale_from_request(request))})
        pass
    user = await UserRepository(session).get_by_username(payload.username)
    if user is None or not verify_password(payload.password, user.password_hash):
        raise auth_error(request, "invalid_credentials")
    return TokenResponse(access_token=create_access_token(str(user.id)), refresh_token=create_refresh_token(str(user.id)))


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: Request, payload: RefreshRequest, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    try:
        claims = await decode_token(payload.refresh_token, expected_type="refresh")
        user = await UserRepository(session).get_by_id(int(claims["sub"]))
        if user is None or not user.is_active:
            raise ValueError("inactive user")
        await revoke_refresh_token(payload.refresh_token)
        return TokenResponse(access_token=create_access_token(str(user.id)), refresh_token=create_refresh_token(str(user.id)))
    except RedisSecurityStateUnavailable:
        raise HTTPException(status_code=503, detail={"code": "security_state_unavailable", "message": translate("errors", "security_state_unavailable", locale_from_request(request))})
    except (KeyError, TypeError, ValueError):
        raise auth_error(request, "invalid_refresh_token")


@router.post("/revoke", status_code=status.HTTP_204_NO_CONTENT)
async def revoke(request: Request, payload: RevokeRequest) -> Response:
    try:
        await revoke_refresh_token(payload.refresh_token)
    except RedisSecurityStateUnavailable:
        raise HTTPException(status_code=503, detail={"code": "security_state_unavailable", "message": translate("errors", "security_state_unavailable", locale_from_request(request))})
    except ValueError:
        raise auth_error(request, "invalid_refresh_token")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=CurrentUserRead)
async def current_user(user: User = Depends(get_current_user)) -> CurrentUserRead:
    return CurrentUserRead(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        permissions=sorted({permission.code for role in user.roles for permission in role.permissions}),
    )
