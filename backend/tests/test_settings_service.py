import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models import Role, User, UserRole
from app.schemas.auth import UserRead
from app.schemas.settings import NotificationPreferenceUpdate, SystemSettingsUpdate
from app.services.notification_service import NotificationService
from app.services.settings_service import SettingsService


def _build_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def _seed_founder(db) -> uuid.UUID:
    role = Role(id=uuid.uuid4(), code="founder", name="Founder")
    user = User(id=uuid.uuid4(), email="founder@example.com", password_hash="x", full_name="Founder User", is_active=True)
    db.add_all([role, user])
    db.commit()
    db.add(UserRole(id=uuid.uuid4(), user_id=user.id, role_id=role.id))
    db.commit()
    return user.id


def _user_read(user_id: uuid.UUID) -> UserRead:
    return UserRead(
        id=str(user_id), email="founder@example.com", full_name="Founder User",
        roles=["founder"], is_active=True, created_at=None, updated_at=None,
    )


def test_system_settings_returns_singleton_defaults():
    db = _build_session()
    try:
        service = SettingsService(db)
        settings = service.get_system_settings()
        assert settings.business_name == "Aalam Groups"
        assert settings.default_currency == "INR"

        # calling twice must not create a second row
        settings_again = service.get_system_settings()
        assert settings_again.business_name == settings.business_name
    finally:
        db.close()


def test_founder_can_update_system_settings():
    db = _build_session()
    try:
        founder_id = _seed_founder(db)
        service = SettingsService(db)
        updated = service.update_system_settings(
            SystemSettingsUpdate(support_email="ops@aalamgroups.com", low_stock_default_threshold=15),
            _user_read(founder_id),
        )
        assert updated.support_email == "ops@aalamgroups.com"
        assert updated.low_stock_default_threshold == 15
        assert updated.business_name == "Aalam Groups"  # untouched fields preserved
    finally:
        db.close()


def test_notification_preference_defaults_to_enabled():
    db = _build_session()
    try:
        founder_id = _seed_founder(db)
        service = SettingsService(db)
        prefs = service.get_notification_preferences(_user_read(founder_id))
        assert prefs.notify_orders is True
        assert prefs.notify_stock is True
    finally:
        db.close()


def test_disabling_stock_preference_suppresses_low_stock_notifications():
    db = _build_session()
    try:
        founder_id = _seed_founder(db)
        current_user = _user_read(founder_id)
        settings_service = SettingsService(db)
        settings_service.update_notification_preferences(NotificationPreferenceUpdate(notify_stock=False), current_user)

        notif_service = NotificationService(db)
        created = notif_service.notify_role("founder", type="low_stock", title="Low stock", message="test")
        assert created == []

        # orders category is still enabled by default
        created_orders = notif_service.notify_role("founder", type="order_created", title="New order", message="test")
        assert len(created_orders) == 1
    finally:
        db.close()
