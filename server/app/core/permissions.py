from fastapi import Depends, HTTPException, Request, status

from server.app.core.i18n import locale_from_request, translate
from server.app.modules.users.model import User


def user_has_permission(user: User, code: str) -> bool:
    return any(permission.code == code for role in user.roles for permission in role.permissions)


def user_data_scope(user: User) -> str:
    return "all" if any(role.data_scope == "all" for role in user.roles) else "self"


def can_access_user(user: User, user_id: int) -> bool:
    return user_data_scope(user) == "all" or user.id == user_id


def require_permission(code: str):
    from server.app.modules.auth.router import get_current_user

    async def dependency(request: Request, user: User = Depends(get_current_user)) -> User:
        if not user_has_permission(user, code):
            locale = locale_from_request(request)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "permission_denied", "message": translate("modules/auth", "permission_denied", locale)},
            )
        return user

    return dependency
