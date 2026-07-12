from __future__ import annotations

import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.settings_repository import SettingsRepository
from app.schemas.auth import UserRead
from app.schemas.settings import (
    NotificationPreferenceRead,
    NotificationPreferenceUpdate,
    SystemSettingsRead,
    SystemSettingsUpdate,
)


def _is_founder(user: UserRead) -> bool:
    return "founder" in user.roles or "super_admin" in user.roles


class SettingsService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SettingsRepository(db)

    def get_system_settings(self) -> SystemSettingsRead:
        settings = self.repo.get_system_settings()
        return SystemSettingsRead.model_validate(settings)

    def update_system_settings(self, payload: SystemSettingsUpdate, current_user: UserRead) -> SystemSettingsRead:
        if not _is_founder(current_user):
            raise HTTPException(status_code=403, detail="Only founders can update system settings")
        settings = self.repo.get_system_settings()
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(settings, key, value)
        settings = self.repo.save_system_settings(settings)
        return SystemSettingsRead.model_validate(settings)

    def get_notification_preferences(self, current_user: UserRead) -> NotificationPreferenceRead:
        preference = self.repo.get_or_create_preference(uuid.UUID(current_user.id))
        return NotificationPreferenceRead.model_validate(preference)

    def update_notification_preferences(self, payload: NotificationPreferenceUpdate, current_user: UserRead) -> NotificationPreferenceRead:
        preference = self.repo.get_or_create_preference(uuid.UUID(current_user.id))
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(preference, key, value)
        preference = self.repo.save_preference(preference)
        return NotificationPreferenceRead.model_validate(preference)
