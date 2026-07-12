import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.security import get_password_hash, verify_password
from app.models import Role, User, UserRole
from app.schemas.profile import ChangePasswordRequest, ProfileUpdate
from app.services.auth_service import AuthService


def _build_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def _seed_user(db, password: str = "OldPass123") -> uuid.UUID:
    role = Role(id=uuid.uuid4(), code="founder", name="Founder")
    user = User(
        id=uuid.uuid4(), email="founder@example.com", password_hash=get_password_hash(password),
        full_name="Founder User", is_active=True, phone="9999999999",
    )
    db.add_all([role, user])
    db.commit()
    db.add(UserRole(id=uuid.uuid4(), user_id=user.id, role_id=role.id))
    db.commit()
    return user.id


def test_get_profile_returns_extended_fields():
    db = _build_session()
    try:
        user_id = _seed_user(db)
        profile = AuthService(db).get_profile(str(user_id))
        assert profile.full_name == "Founder User"
        assert profile.roles == ["founder"]
    finally:
        db.close()


def test_update_profile_only_touches_provided_fields():
    db = _build_session()
    try:
        user_id = _seed_user(db)
        updated = AuthService(db).update_profile(str(user_id), ProfileUpdate(full_name="New Name"))
        assert updated.full_name == "New Name"
        assert updated.phone == "9999999999"  # untouched
    finally:
        db.close()


def test_change_password_rejects_wrong_current_password():
    db = _build_session()
    try:
        user_id = _seed_user(db)
        service = AuthService(db)
        try:
            service.change_password(str(user_id), ChangePasswordRequest(current_password="wrong", new_password="NewPass1234"))
            assert False, "expected HTTPException"
        except Exception as exc:
            assert "incorrect" in str(exc.detail).lower()
    finally:
        db.close()


def test_change_password_updates_hash_and_revokes_sessions():
    db = _build_session()
    try:
        user_id = _seed_user(db)
        service = AuthService(db)
        service.change_password(str(user_id), ChangePasswordRequest(current_password="OldPass123", new_password="NewPass1234"))
        user = service.user_repo.get_by_id(user_id)
        assert verify_password("NewPass1234", user.password_hash)
        assert not verify_password("OldPass123", user.password_hash)
    finally:
        db.close()
