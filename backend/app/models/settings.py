import uuid
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

# Fixed primary key so the settings table always has exactly one row.
SYSTEM_SETTINGS_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


class SystemSettings(BaseModel):
    __tablename__ = "system_settings"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=lambda: SYSTEM_SETTINGS_ID)
    business_name: Mapped[str] = mapped_column(String(200), default="Aalam Groups", nullable=False)
    support_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    support_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    gst_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    default_currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    low_stock_default_threshold: Mapped[int] = mapped_column(default=10, nullable=False)
    invoice_footer_note: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)


class NotificationPreference(BaseModel):
    __tablename__ = "notification_preferences"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    notify_orders: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_dispatch: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_stock: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notify_system: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id])


from app.models.user import User  # noqa: E402
