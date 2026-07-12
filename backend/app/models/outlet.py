import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Outlet(BaseModel):
    __tablename__ = "outlets"
    __table_args__ = (
        Index("ix_outlets_shop_name", "shop_name"),
        Index("ix_outlets_area_city", "area", "city"),
        Index("ix_outlets_status", "status"),
        Index("ix_outlets_assigned_distributor_id", "assigned_distributor_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    outlet_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    shop_name: Mapped[str] = mapped_column(String(200), nullable=False)
    owner_name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    whatsapp_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    gst_number: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    area: Mapped[str] = mapped_column(String(120), nullable=False)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    district: Mapped[str] = mapped_column(String(120), nullable=False)
    state: Mapped[str] = mapped_column(String(120), nullable=False)
    pincode: Mapped[str] = mapped_column(String(10), nullable=False)
    territory: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    google_maps_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    business_type: Mapped[str] = mapped_column(String(50), nullable=False)
    brands: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    assigned_distributor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    qr_code_value: Mapped[str] = mapped_column(String(255), nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("users.id"), nullable=True)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("users.id"), nullable=True)

    assigned_distributor: Mapped[Optional["User"]] = relationship(
        "User", foreign_keys=[assigned_distributor_id]
    )
    visits: Mapped[list["OutletVisit"]] = relationship(
        "OutletVisit", back_populates="outlet", cascade="all, delete-orphan"
    )
    photos: Mapped[list["OutletPhoto"]] = relationship(
        "OutletPhoto", back_populates="outlet", cascade="all, delete-orphan"
    )
    contacts: Mapped[list["OutletContact"]] = relationship(
        "OutletContact", back_populates="outlet", cascade="all, delete-orphan"
    )


class OutletVisit(BaseModel):
    __tablename__ = "outlet_visits"
    __table_args__ = (
        Index("ix_outlet_visits_outlet_id", "outlet_id"),
        Index("ix_outlet_visits_distributor_id", "distributor_id"),
        Index("ix_outlet_visits_visit_date", "visit_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    outlet_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("outlets.id", ondelete="CASCADE"), nullable=False
    )
    visit_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    distributor_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("users.id"), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    next_follow_up_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("users.id"), nullable=True)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("users.id"), nullable=True)

    outlet: Mapped["Outlet"] = relationship("Outlet", back_populates="visits")
    distributor: Mapped[Optional["User"]] = relationship("User", foreign_keys=[distributor_id])


class OutletPhoto(BaseModel):
    __tablename__ = "outlet_photos"
    __table_args__ = (
        Index("ix_outlet_photos_outlet_id", "outlet_id"),
        Index("ix_outlet_photos_photo_type", "photo_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    outlet_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("outlets.id", ondelete="CASCADE"), nullable=False
    )
    photo_type: Mapped[str] = mapped_column(String(30), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("users.id"), nullable=True)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("users.id"), nullable=True)

    outlet: Mapped["Outlet"] = relationship("Outlet", back_populates="photos")


class OutletContact(BaseModel):
    __tablename__ = "outlet_contacts"
    __table_args__ = (Index("ix_outlet_contacts_outlet_id", "outlet_id"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    outlet_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("outlets.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    role: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    whatsapp: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("users.id"), nullable=True)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("users.id"), nullable=True)

    outlet: Mapped["Outlet"] = relationship("Outlet", back_populates="contacts")


from app.models.user import User  # noqa: E402
