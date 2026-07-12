from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models import NotificationPreference, SystemSettings
from app.models.settings import SYSTEM_SETTINGS_ID


class SettingsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_system_settings(self) -> SystemSettings:
        settings = self.db.query(SystemSettings).filter(SystemSettings.id == SYSTEM_SETTINGS_ID).first()
        if not settings:
            settings = SystemSettings(id=SYSTEM_SETTINGS_ID)
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
        return settings

    def save_system_settings(self, settings: SystemSettings) -> SystemSettings:
        self.db.add(settings)
        self.db.commit()
        self.db.refresh(settings)
        return settings

    def get_or_create_preference(self, user_id: uuid.UUID) -> NotificationPreference:
        preference = self.db.query(NotificationPreference).filter(NotificationPreference.user_id == user_id).first()
        if not preference:
            preference = NotificationPreference(id=uuid.uuid4(), user_id=user_id)
            self.db.add(preference)
            self.db.commit()
            self.db.refresh(preference)
        return preference

    def save_preference(self, preference: NotificationPreference) -> NotificationPreference:
        self.db.add(preference)
        self.db.commit()
        self.db.refresh(preference)
        return preference
