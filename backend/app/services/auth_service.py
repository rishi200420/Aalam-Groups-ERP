import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    hash_token,
    verify_password,
    verify_token,
)
from app.models import User
from app.repositories.auth_repository import RefreshTokenRepository, UserRepository
from app.schemas.auth import LoginRequest, LoginResponse, RefreshTokenRequest, UserRead
from app.schemas.profile import ChangePasswordRequest, ProfileRead, ProfileUpdate


def _as_utc(value: datetime) -> datetime:
    """SQLite does not persist tzinfo, so naive datetimes read back from the DB
    are assumed to be UTC (which is how they were written)."""
    return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = RefreshTokenRepository(db)

    def _serialize_user(self, user: User) -> UserRead:
        return UserRead(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            roles=user.role_codes,
            primary_role=user.primary_role,
            is_active=user.is_active,
        )

    def login(self, payload: LoginRequest) -> LoginResponse:
        user = self.user_repo.get_by_email(payload.email.lower())

        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive. Contact administrator.",
            )

        access_token = create_access_token(
            subject=str(user.id),
            extra_claims={"role": user.primary_role, "email": user.email},
        )
        refresh_token = create_refresh_token(subject=str(user.id))
        refresh_payload = verify_token(refresh_token, token_type="refresh")

        if not refresh_payload or "exp" not in refresh_payload:
            raise HTTPException(status_code=500, detail="Failed to create refresh token")

        expires_at = datetime.fromtimestamp(refresh_payload["exp"], tz=timezone.utc)
        self.token_repo.create(
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            expires_at=expires_at,
        )

        self.user_repo.update_last_login(user)

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=self._serialize_user(user),
        )

    def refresh(self, payload: RefreshTokenRequest) -> LoginResponse:
        token_payload = verify_token(payload.refresh_token, token_type="refresh")
        if not token_payload:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        stored = self.token_repo.get_by_hash(hash_token(payload.refresh_token))
        if not stored or stored.revoked_at is not None or _as_utc(stored.expires_at) < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Refresh token expired or revoked")

        user = self.user_repo.get_by_id(stored.user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="User not found or inactive")

        self.token_repo.revoke(stored)

        access_token = create_access_token(
            subject=str(user.id),
            extra_claims={"role": user.primary_role, "email": user.email},
        )
        new_refresh_token = create_refresh_token(subject=str(user.id))
        refresh_payload = verify_token(new_refresh_token, token_type="refresh")

        if not refresh_payload or "exp" not in refresh_payload:
            raise HTTPException(status_code=500, detail="Failed to create refresh token")

        expires_at = datetime.fromtimestamp(refresh_payload["exp"], tz=timezone.utc)
        self.token_repo.create(
            user_id=user.id,
            token_hash=hash_token(new_refresh_token),
            expires_at=expires_at,
        )

        return LoginResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            user=self._serialize_user(user),
        )

    def logout(self, user_id: str, refresh_token: str | None = None) -> None:
        if refresh_token:
            stored = self.token_repo.get_by_hash(hash_token(refresh_token))
            if stored and str(stored.user_id) == user_id and stored.revoked_at is None:
                self.token_repo.revoke(stored)
                return

        self.token_repo.revoke_all_for_user(uuid.UUID(user_id))

    def get_current_user(self, user_id: str) -> UserRead:
        user = self.user_repo.get_by_id(uuid.UUID(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is inactive")
        return self._serialize_user(user)

    def request_password_reset(self, email: str) -> None:
        # Placeholder for future email integration
        user = self.user_repo.get_by_email(email.lower())
        if not user:
            return
        # No-op for now — prevents email enumeration in response

    def _serialize_profile(self, user: User) -> ProfileRead:
        return ProfileRead(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            phone=user.phone,
            roles=user.role_codes,
            primary_role=user.primary_role,
            is_active=user.is_active,
            employee_id=user.employee_id,
            distributor_code=user.distributor_code,
            territory=user.territory,
            brand=user.brand,
            joining_date=user.joining_date,
            profile_image_url=user.profile_image_url,
            last_login_at=user.last_login_at,
            created_at=user.created_at,
        )

    def get_profile(self, user_id: str) -> ProfileRead:
        user = self.user_repo.get_by_id(uuid.UUID(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return self._serialize_profile(user)

    def update_profile(self, user_id: str, payload: ProfileUpdate) -> ProfileRead:
        user = self.user_repo.get_by_id(uuid.UUID(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return self._serialize_profile(user)

    def change_password(self, user_id: str, payload: ChangePasswordRequest) -> None:
        user = self.user_repo.get_by_id(uuid.UUID(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if not verify_password(payload.current_password, user.password_hash):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        user.password_hash = get_password_hash(payload.new_password)
        self.db.add(user)
        self.db.commit()
        # Changing your own password invalidates all existing sessions.
        self.token_repo.revoke_all_for_user(uuid.UUID(user_id))

    def set_avatar(self, user_id: str, avatar_url: str) -> ProfileRead:
        user = self.user_repo.get_by_id(uuid.UUID(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.profile_image_url = avatar_url
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return self._serialize_profile(user)
