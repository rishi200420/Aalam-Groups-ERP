from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.schemas.auth import UserRead
from app.schemas.common import APIResponse
from app.schemas.settings import (
    NotificationPreferenceRead,
    NotificationPreferenceUpdate,
    SystemSettingsRead,
    SystemSettingsUpdate,
)
from app.services.settings_service import SettingsService

router = APIRouter()


@router.get("/status")
async def settings_module_status():
    return {"module": "settings", "status": "ready"}


@router.get("/system", response_model=APIResponse[SystemSettingsRead])
async def get_system_settings(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="System settings retrieved", data=SettingsService(db).get_system_settings())


@router.put("/system", response_model=APIResponse[SystemSettingsRead])
async def update_system_settings(
    payload: SystemSettingsUpdate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="System settings updated", data=SettingsService(db).update_system_settings(payload, current_user))


@router.get("/notification-preferences", response_model=APIResponse[NotificationPreferenceRead])
async def get_notification_preferences(
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(success=True, message="Notification preferences retrieved", data=SettingsService(db).get_notification_preferences(current_user))


@router.put("/notification-preferences", response_model=APIResponse[NotificationPreferenceRead])
async def update_notification_preferences(
    payload: NotificationPreferenceUpdate,
    current_user: Annotated[UserRead, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    return APIResponse(
        success=True,
        message="Notification preferences updated",
        data=SettingsService(db).update_notification_preferences(payload, current_user),
    )
