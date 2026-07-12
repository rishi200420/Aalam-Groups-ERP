import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

DISPATCH_STATUSES = ("ready", "dispatched", "in_transit", "delivered", "failed", "returned")


class Dispatch(BaseModel):
    __tablename__ = "dispatches"
    __table_args__ = (
        Index("ix_dispatches_order_id", "order_id"),
        Index("ix_dispatches_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    dispatch_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    order_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("orders.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="ready", nullable=False)
    tracking_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    courier_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("users.id"), nullable=True)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("users.id"), nullable=True)

    order: Mapped["Order"] = relationship("Order")
    items: Mapped[list["DispatchItem"]] = relationship(
        "DispatchItem", back_populates="dispatch", cascade="all, delete-orphan"
    )
    timelines: Mapped[list["DispatchTimeline"]] = relationship(
        "DispatchTimeline", back_populates="dispatch", cascade="all, delete-orphan"
    )


class DispatchItem(BaseModel):
    __tablename__ = "dispatch_items"
    __table_args__ = (Index("ix_dispatch_items_dispatch_id", "dispatch_id"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    dispatch_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("dispatches.id", ondelete="CASCADE"), nullable=False
    )
    order_item_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid, ForeignKey("order_items.id"), nullable=True
    )
    product_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    line_total: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    dispatch: Mapped["Dispatch"] = relationship("Dispatch", back_populates="items")
    product: Mapped["Product"] = relationship("Product")


class DispatchTimeline(BaseModel):
    __tablename__ = "dispatch_timelines"
    __table_args__ = (Index("ix_dispatch_timelines_dispatch_id", "dispatch_id"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    dispatch_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("dispatches.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    changed_by: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("users.id"), nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    dispatch: Mapped["Dispatch"] = relationship("Dispatch", back_populates="timelines")


from app.models.order import Order  # noqa: E402
from app.models.product import Product  # noqa: E402
from app.models.user import User  # noqa: E402
