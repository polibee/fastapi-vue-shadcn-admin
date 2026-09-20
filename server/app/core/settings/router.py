from fastapi import APIRouter, Depends

from server.app.core.config import get_settings
from server.app.core.rate_limit import api_rate_limit
from server.app.modules.auth.router import get_current_user
from server.app.modules.users.model import User
from .schema import SettingsRead, build_settings_snapshot

router = APIRouter(prefix="/api/v1/settings", tags=["Settings"], dependencies=[api_rate_limit("settings")])


@router.get("", response_model=SettingsRead)
async def read_settings(
    _: User = Depends(get_current_user),
) -> SettingsRead:
    return SettingsRead.model_validate(build_settings_snapshot(get_settings()))
