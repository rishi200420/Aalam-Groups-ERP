import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Date, ForeignKey, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.role import Role
    from app.models.refresh_token import RefreshToken


class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    employee_id: Mapped[Optional[str]] = mapped_column(String(40), unique=True, nullable=True)
    distributor_code: Mapped[Optional[str]] = mapped_column(String(40), unique=True, nullable=True)
    territory: Mapped[Optional[str]] = mapped_column(String(120), nullable=True, index=True)
    brand: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    joining_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    profile_image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("users.id"), nullable=True)

    user_roles: Mapped[List["UserRole"]] = relationship(
        "UserRole", back_populates="user", cascade="all, delete-orphan", foreign_keys="[UserRole.user_id]"
    )
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def roles(self) -> List["Role"]:
        return [ur.role for ur in self.user_roles if ur.role is not None]

    @property
    def role_codes(self) -> List[str]:
        return [role.code for role in self.roles]

    @property
    def primary_role(self) -> Optional[str]:
        if not self.roles:
            return None
        priority = ["super_admin", "founder", "distributor", "warehouse", "sales_executive"]
        codes = self.role_codes
        for code in priority:
            if code in codes:
                return code
        return codes[0]


class UserRole(BaseModel):
    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="user_roles")
    role: Mapped["Role"] = relationship("Role", back_populates="user_roles")
