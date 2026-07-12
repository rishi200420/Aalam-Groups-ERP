import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models import Role, User, UserRole
from app.schemas.auth import UserRead
from app.services.notification_service import NotificationService


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


def test_notify_role_creates_notification_for_matching_users():
    db = _build_session()
    try:
        founder_id = _seed_founder(db)
        service = NotificationService(db)
        created = service.notify_role("founder", type="system", title="Test", message="Hello founder")
        assert len(created) == 1
        assert created[0].user_id == founder_id

        summary = service.unread_count(_user_read(founder_id))
        assert summary.unread_count == 1
    finally:
        db.close()


def test_mark_read_and_mark_all_read_flow():
    db = _build_session()
    try:
        founder_id = _seed_founder(db)
        current_user = _user_read(founder_id)
        service = NotificationService(db)
        service.notify_role("founder", type="system", title="One", message="msg1")
        service.notify_role("founder", type="system", title="Two", message="msg2")

        listing = service.list_notifications(current_user, page=1, page_size=10)
        assert listing.total == 2
        assert service.unread_count(current_user).unread_count == 2

        first = listing.data[0]
        service.mark_read(uuid.UUID(first.id), current_user)
        assert service.unread_count(current_user).unread_count == 1

        marked = service.mark_all_read(current_user)
        assert marked == 1
        assert service.unread_count(current_user).unread_count == 0
    finally:
        db.close()


def test_delete_notification_removes_it():
    db = _build_session()
    try:
        founder_id = _seed_founder(db)
        current_user = _user_read(founder_id)
        service = NotificationService(db)
        service.notify_role("founder", type="system", title="One", message="msg1")

        listing = service.list_notifications(current_user, page=1, page_size=10)
        notification_id = uuid.UUID(listing.data[0].id)
        service.delete_notification(notification_id, current_user)

        listing_after = service.list_notifications(current_user, page=1, page_size=10)
        assert listing_after.total == 0
    finally:
        db.close()
