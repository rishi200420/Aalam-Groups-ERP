import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session, joinedload

from app.models import RefreshToken, User, UserRole


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return (
            self.db.query(User)
            .options(
                joinedload(User.user_roles).joinedload(UserRole.role),
            )
            .filter(User.email == email.lower())
            .first()
        )

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return (
            self.db.query(User)
            .options(
                joinedload(User.user_roles).joinedload(UserRole.role),
            )
            .filter(User.id == user_id)
            .first()
        )

    def update_last_login(self, user: User) -> None:
        user.last_login_at = datetime.now(timezone.utc)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)


class RefreshTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: uuid.UUID, token_hash: str, expires_at: datetime) -> RefreshToken:
        token = RefreshToken(
            id=uuid.uuid4(),
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)
        return token

    def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        return self.db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()

    def revoke(self, token: RefreshToken) -> None:
        token.revoked_at = datetime.now(timezone.utc)
        self.db.add(token)
        self.db.commit()

    def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        tokens = (
            self.db.query(RefreshToken)
            .filter(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
            .all()
        )
        now = datetime.now(timezone.utc)
        for token in tokens:
            token.revoked_at = now
            self.db.add(token)
        self.db.commit()
